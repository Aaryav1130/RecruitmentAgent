import sys
import os
import logging

# Load .env from project root (where GROQ_API_KEY lives)
from dotenv import load_dotenv
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(root_dir, ".env"))
load_dotenv()  # Also load Interview-local .env if present

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger("interview-agent")

from livekit.plugins import groq
from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io, inference, ToolError, RunContext, function_tool
from livekit.plugins import silero
from livekit.plugins import bey
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from typing import Annotated
import json

# Import dynamic model from config
sys.path.append(root_dir)
from config import LLM_MODEL

logger.info(f"GROQ_API_KEY set: {bool(os.getenv('GROQ_API_KEY'))}")
logger.info(f"LIVEKIT_URL: {os.getenv('LIVEKIT_URL', 'NOT SET')}")
logger.info(f"BEY_API_KEY set: {bool(os.getenv('BEY_API_KEY'))}")
logger.info(f"BEY_AVATAR_ID: {os.getenv('BEY_AVATAR_ID', 'NOT SET')}")
logger.info(f"LLM_MODEL: {LLM_MODEL}")

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
        )

server = AgentServer()

@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    logger.info("[AGENT] Creating session...")

    session = AgentSession(
        stt=groq.STT(model="whisper-large-v3-turbo", language="en"),
        llm=groq.LLM(model=LLM_MODEL),
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

    logger.info("[AGENT] Starting Bey avatar...")
    avatar = bey.AvatarSession(
        avatar_id=os.getenv("BEY_AVATAR_ID"),
    )
    await avatar.start(session, room=ctx.room)

    logger.info("[AGENT] Starting agent session...")
    await session.start(
        room=ctx.room,
        agent=Assistant(),
    )

    logger.info("[AGENT] Generating initial reply...")
    await session.generate_reply(
        instructions=SESSION_INSTRUCTION
    )
    logger.info("[AGENT] Initial reply sent!")


if __name__ == "__main__":
    agents.cli.run_app(server)
