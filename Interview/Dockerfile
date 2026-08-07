# ── Stage: Flask Token Server + LiveKit Agent ────────────────────────
FROM python:3.13-slim

# Install uv (fast Python package manager)
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy dependency manifests from the project root (needed for shared deps)
COPY pyproject.toml uv.lock ./

# Install production dependencies only
RUN uv sync --no-dev

# Copy Interview source code
COPY Interview/ ./Interview/

WORKDIR /app/Interview

EXPOSE 5001

CMD ["uv", "run", "python", "livekit_token.py"]
