# Backend Dockerfile for The Holding Cell
# Per D-02: FastAPI + Socket.io backend for real-time attack visualization
# Per D-09: Health check via curl to /health endpoint
# Per SEC-01: Run as non-root user for security

# Base image: Python 3.11 slim for minimal size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# Per D-09: curl required for Docker health checks
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Per SEC-01: Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Copy Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Per SEC-01: Create data directory with proper ownership for persistence volume
RUN mkdir -p /data && chown -R appuser:appgroup /data

# Expose port 8000 (can bind as non-root since > 1024)
EXPOSE 8000

# Health check - uses /health endpoint from main.py
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Per SEC-01: Switch to non-root user
USER appuser

# Start uvicorn with combined_app (FastAPI + Socket.io ASGI app)
# Use combined_app, not app, to include Socket.io
CMD ["uvicorn", "main:combined_app", "--host", "0.0.0.0", "--port", "8000"]