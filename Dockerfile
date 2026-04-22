# ============================================================
# StellarBot Production Dockerfile - Multi-stage Build
# Optimized for security, size, and performance
# Features:
#   - Minimal base image (python:3.11-slim)
#   - Multi-stage build for lean production image
#   - Health checks
#   - Non-root user for security
#   - Async/await support with improved error handling
# ============================================================

# --- Stage 1: Builder ---
FROM python:3.11-slim as builder

LABEL maintainer="StellarBot Team"
LABEL description="StellarBot - Enterprise Trading Bot for Stellar DEX"

# Build environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build dependencies (minimal set)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Build wheels for dependencies
RUN pip install --user \
    --no-warn-script-location \
    --requirement requirements.txt


# --- Stage 2: Runtime ---
FROM python:3.11-slim

LABEL version="2.0"
LABEL maintainer="StellarBot Team"

# Security: Non-root user
RUN groupadd -r stellarbot && useradd -r -g stellarbot -u 1000 stellarbot

# Production environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH=/home/stellarbot/.local/bin:$PATH \
    LOG_LEVEL=INFO \
    ENVIRONMENT=production \
    STELLARBOT_ENV=production

# Install minimal runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    libssl3 \
    libffi8 \
    && rm -rf /var/lib/apt/lists/*

# Create application directories
RUN mkdir -p /app /data /logs && \
    chown -R stellarbot:stellarbot /app /data /logs

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder --chown=stellarbot:stellarbot /root/.local /home/stellarbot/.local

# Copy application code
COPY --chown=stellarbot:stellarbot . .

# Switch to non-root user
USER stellarbot

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port for API (future use)
EXPOSE 8000

# Entry point
ENTRYPOINT ["python", "-u", "stellarbot_app.py"]
CMD ["--debug"]

    x11-apps \
    xauth \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    fonts-dejavu \
    libqt5gui5 \
    libqt5widgets5 \
    libdbus-1-3 \
    libfontconfig1 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder --chown=stellarbot:stellarbot /root/.local /home/stellarbot/.local

# Copy application code
COPY --chown=stellarbot:stellarbot src/ ./src/
COPY --chown=stellarbot:stellarbot config.yaml ./
COPY --chown=stellarbot:stellarbot stellarbot.py ./
COPY --chown=stellarbot:stellarbot .env.example ./

# Create VNC password directory
RUN mkdir -p /home/stellarbot/.vnc && chown -R stellarbot:stellarbot /home/stellarbot/.vnc

# Create entrypoint script
COPY --chown=stellarbot:stellarbot docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Ensure binary path is in PATH
ENV PATH=/home/stellarbot/.local/bin:$PATH

# Ports:
# 8000 - Application API
# 5900 - VNC Server
# 6080 - NoVNC Web Interface
EXPOSE 8000 5900 6080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:6080 || exit 1

# Switch to non-root user
USER stellarbot

# Run entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]


