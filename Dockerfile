FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libxcb1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
COPY pyproject.toml .
RUN uv pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cu121
RUN uv pip install --no-cache-dir -r pyproject.toml
COPY . .

EXPOSE 8000

CMD ["python", "-m", "app.main"]