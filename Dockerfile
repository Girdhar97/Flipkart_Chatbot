## Builder stage
FROM python:3.11 AS builder
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y build-essential curl \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

## Runtime stage
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

## Copy wheels/runtime from builder (slim image)
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

RUN useradd --create-home appuser && chown -R appuser:appuser /app \
    && apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/* \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Healthcheck with logging
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# CMD with logging setup
CMD ["/bin/bash", "-c", "echo 'Starting RAG Chatbot container...' && python app.py"]
