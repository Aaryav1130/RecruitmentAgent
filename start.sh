#!/bin/bash

echo "Starting Streamlit..."
uv run streamlit run main.py &

echo "Starting LiveKit Agent..."
cd Interview
uv run python agent_runner.py dev &

echo "Starting Flask Token API..."
uv run python livekit_token.py &

echo "Starting React Frontend..."
cd frontend
npm run dev &

echo "All services started!"
wait
