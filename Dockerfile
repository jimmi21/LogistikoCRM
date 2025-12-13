# ============================================================================
# D.P. Economy - Production Dockerfile
# ============================================================================

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /code

# Install Python dependencies
COPY requirements.txt setup.cfg ./
RUN pip install --upgrade pip && \
    pip install -e .

# Copy project files
COPY . .

# Create media and static directories
RUN mkdir -p /code/media /code/staticfiles

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000', timeout=5)"

# Entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "webcrm.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
