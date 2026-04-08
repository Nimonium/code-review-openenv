FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if any are needed (e.g., git)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Permissions for Hugging Face Spaces (user 1000)
RUN chmod -R 777 /app

# HF Spaces uses port 7860 by default, but we should use the PORT env var
ENV PORT=7860
ENV PYTHONPATH=/app
EXPOSE 7860

# Run with standard uvicorn to support websockets (for /ws endpoint)
CMD ["sh", "-c", "uvicorn server.app:app --host 0.0.0.0 --port ${PORT}"]