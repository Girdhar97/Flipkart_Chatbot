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

# Used PORTS (FIX: match app.py)
EXPOSE 8000

# Run the app 
CMD ["python", "app.py"]
