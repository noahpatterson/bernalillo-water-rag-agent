FROM python:3.13-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock README.md ./
COPY utils ./utils
COPY tools ./tools
COPY embedder.py main.py ./

RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD [".venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
