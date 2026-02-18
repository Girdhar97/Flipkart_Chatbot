## Parent image
FROM python:3.11-slim

## Essential environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

## Work directory inside the docker container
WORKDIR /app

## Installing system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

## Copy requirements first (NEW: enables layer caching)
COPY requirements.txt .

## Install Python deps (NEW: --upgrade + no-cache)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

## Copy app contents
COPY . .

## Create non-root user (NEW: security)
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app
USER appuser

# Used PORTS
EXPOSE 8000

## Healthcheck (NEW: for K8s liveness)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the app 
CMD ["python", "app.py"]
