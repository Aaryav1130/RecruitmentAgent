# ── Stage: Streamlit App ──────────────────────────────────────────────
FROM python:3.13-slim

# System dependencies (LaTeX for resume generation, build tools for native packages)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        texlive-xetex \
        texlive-fonts-recommended \
        build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager)
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy dependency manifests first for layer caching
COPY pyproject.toml uv.lock ./

# Install production dependencies only
RUN uv sync --no-dev

# Copy application source code
COPY agents/ ./agents/
COPY utils/ ./utils/
COPY main.py config.py ui_utils.py ./
COPY Images/ ./Images/

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
