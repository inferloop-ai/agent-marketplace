# Agent Engine Backend Dockerfile
# =======================================

# This Dockerfile creates a production-ready container for the Agent Engine backend service
# using a multi-stage build process to minimize image size and enhance security.

# Build Instructions
# -----------------
# 1. Build the Docker image:
#    docker build -t agent-engine .

# 2. Run the container:
#    docker run -d -p 8000:8000 agent-engine

# 3. Access the API:
#    http://localhost:8000/docs (Swagger UI)
#    http://localhost:8000/redoc (ReDoc)

# 4. Health check:
#    curl http://localhost:8000/health

# 5. Environment Variables:
#    - DATABASE_URL: Database connection string
#    - OPENAI_API_KEY: OpenAI API key
#    - REDIS_URL: Redis connection string (optional)

# 6. Volume Mounts:
#    - /app/data: Persistent data storage
#    - /app/logs: Application logs

# Stage 1: Build
# -------------
# Uses Python 3.11 slim image to build the application and install dependencies
FROM python:3.11-slim as builder

# Set environment variables for optimal performance and security
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install build dependencies required for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Production
# -------------------
# Uses a minimal Python image for production
FROM python:3.11-slim

# Install minimal system dependencies required for production
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Copy dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose default port
EXPOSE 8000

# Default command to run the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Health check configuration
# -------------------------
# - Interval: 30 seconds
# - Timeout: 3 seconds
# - Start period: 5 seconds
# - Retries: 3
# - Checks: /health endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Additional Notes
# ---------------
# 1. The container uses uvicorn as the ASGI server
# 2. Health checks are enabled to monitor container status
# 3. All Python dependencies are installed in a separate build stage
# 4. The final image is minimal and runs as non-root user
# 5. No unnecessary files are included in the final image
# 6. The container is optimized for production use

# Troubleshooting
# --------------
# 1. If the container fails to start:
#    - Check logs: docker logs <container_id>
#    - Verify environment variables are set
#    - Check port conflicts

# 2. If health checks fail:
#    - Verify the health endpoint is properly implemented
#    - Check network connectivity
#    - Verify the application is running