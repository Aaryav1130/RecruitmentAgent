#!/bin/bash

echo "Starting Streamlit..."
uv run streamlit run main.py &

echo "Starting LiveKit Agent..."
cd interview
uv run agent_runner.py dev &

echo "Starting Flask Token API..."
uv run livekit_token.py &

echo "Starting React Frontend..."
cd frontend
npm run dev &

echo "All services started!"
wait
