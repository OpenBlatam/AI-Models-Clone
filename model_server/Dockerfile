FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy minimal requirements for inference
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy code
COPY src /app/src
COPY model_server /app/model_server

EXPOSE 8000

ENV HOST=0.0.0.0 PORT=8000 WORKERS=1 LOG_LEVEL=info

CMD ["uvicorn", "model_server.app:app", "--host", "0.0.0.0", "--port", "8000"]



