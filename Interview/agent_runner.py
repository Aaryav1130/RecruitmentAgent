from dotenv import load_dotenv
from livekit.plugins import groq
from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io, inference, ToolError, RunContext,function_tool
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from livekit.plugins import bey
from typing import Annotated
import json
import logging
import os

load_dotenv()

class Assistant(Agent):
    def __init__(self) -> None: 
        super().__init__(
            instructions=AGENT_INSTRUCTION,
        )

server = AgentServer()


@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    session = AgentSession(
        stt=groq.STT(model="whisper-large-v3-turbo", language="en"),
        llm=groq.LLM(model="llama-3.1-8b-instant"),
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
        turn_detection=MultilingualModel(),
    )

    avatar = bey.AvatarSession(
        avatar_id=os.getenv("BEY_AVATAR_ID"),  # ID of the Beyond Presence avatar to use
    )

    await avatar.start(session, room=ctx.room)

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony() if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP else noise_cancellation.BVC(),
            ),
            video_input=True
        ),
    )

    await session.generate_reply(
        instructions=SESSION_INSTRUCTION
    )


if __name__ == "__main__":
    agents.cli.run_app(server)
