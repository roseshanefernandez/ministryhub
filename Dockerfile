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

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Create necessary directories and set permissions
RUN mkdir -p /app/staticfiles /app/media/events && \
    chown -R appuser:appgroup /app

# Copy the entrypoint script and set executable permissions
COPY --chown=appuser:appgroup entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy the rest of the application code
COPY --chown=appuser:appgroup . .

# Secure the runtime by switching away from root
USER appuser

ENTRYPOINT ["/app/entrypoint.sh"]