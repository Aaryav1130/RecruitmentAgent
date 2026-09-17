import sys
import os
import logging

# Load .env from project root
from dotenv import load_dotenv
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(root_dir, ".env"))

# Also load Interview-local .env if it exists
load_dotenv()

from livekit.plugins import groq
from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io, inference, ToolError, RunContext, function_tool
from livekit.plugins import silero
from livekit.plugins import bey
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from typing import Annotated
import json

# Enable detailed logging so errors are visible
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("interview-agent")

# Import dynamic model from config
sys.path.append(root_dir)
from config import LLM_MODEL

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
        )

server = AgentServer()

@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    logger.info(f"[AGENT] New session starting, using LLM model: {LLM_MODEL}")

    session = AgentSession(
        # STT: Use LiveKit's hosted inference (uses LiveKit credits, not your Groq quota)
        stt=inference.STT(model="groq/whisper-large-v3-turbo", language="en"),
        # LLM: Use LiveKit's hosted inference (avoids Groq rate limits)
        llm=inference.LLM(model=f"groq/{LLM_MODEL}"),
        # TTS: LiveKit hosted Cartesia
        tts=inference.TTS(
            model="cartesia/sonic-3",
            voice="a167e0f3-df7e-4d52-a9c3-f949145efdab",
            language="en",
            extra_kwargs={
                "speed": 0.7,
                "volume": 2.0,
                "emotion": "calm"
            }
        ),
        vad=silero.VAD.load(),
    )

    logger.info("[AGENT] AgentSession created, starting Bey avatar...")

    avatar = bey.AvatarSession(
        avatar_id=os.getenv("BEY_AVATAR_ID"),
    )

    await avatar.start(session, room=ctx.room)
    logger.info("[AGENT] Bey avatar started, starting session...")

    await session.start(
        room=ctx.room,
        agent=Assistant(),
    )

    logger.info("[AGENT] Session started, generating initial reply...")

    await session.generate_reply(
        instructions=SESSION_INSTRUCTION
    )

    logger.info("[AGENT] Initial reply generated successfully")


if __name__ == "__main__":
    agents.cli.run_app(server)
