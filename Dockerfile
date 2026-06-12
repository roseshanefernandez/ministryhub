# Stage 1: Base build stage
FROM python:3.13-slim AS builder

# Set the working directory
WORKDIR /app

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade pip and install dependencies
RUN pip install --upgrade pip

# Copy the requirements file first (better caching)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Stage 2: Production stage
FROM python:3.13-slim

# Create a system user and group first
RUN groupadd -r appgroup && useradd -r -g appgroup -m appuser

# Set the working directory
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# 1. Copy ALL your source code files first (with proper user ownership flags)
COPY --chown=appuser:appgroup . .

# 2. Perform file tuning and directory creation while still logged in as root
USER root

# Create directories, enforce ownership, and set executable flags cleanly
RUN mkdir -p /app/staticfiles /app/media/events && \
    chown -R appuser:appgroup /app && \
    chmod -R 755 /app/staticfiles /app/media/events && \
    chmod +x /app/entrypoint.sh

# 3. Secure the runtime environment by permanently dropping administrative privileges
USER appuser

ENTRYPOINT ["/app/entrypoint.sh"]
