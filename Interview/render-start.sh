#!/bin/bash
# Install uv if not present
pip install uv

# Sync dependencies
uv sync

# Start the LiveKit agent in the background
uv run python agent_runner.py dev &

# Start the Flask API in the foreground using gunicorn
uv run gunicorn livekit_token:app --bind 0.0.0.0:$PORT
