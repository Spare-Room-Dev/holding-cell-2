# Backend Dockerfile for The Holding Cell
# Per D-02: FastAPI + Socket.io backend for real-time attack visualization
# Per D-09: Health check via curl to /health endpoint

# Base image: Python 3.11 slim for minimal size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# Per D-09: curl required for Docker health checks
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 8000
EXPOSE 8000

# Health check - uses /health endpoint from main.py
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start uvicorn with combined_app (FastAPI + Socket.io ASGI app)
# Use combined_app, not app, to include Socket.io
CMD ["uvicorn", "main:combined_app", "--host", "0.0.0.0", "--port", "8000"]