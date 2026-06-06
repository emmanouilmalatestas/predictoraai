FROM python:3.11-slim

# Set working directory
WORKDIR /app
ENV PYTHONPATH="/app"

# System deps (curl για tests, gcc αν χρειαστεί build)
RUN apt update && apt install -y \
    curl \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir prometheus-fastapi-instrumentator

# Copy app
COPY . /app

# Non-root user
RUN useradd -m appuser \
 && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Healthcheck (χτυπάει /health)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
