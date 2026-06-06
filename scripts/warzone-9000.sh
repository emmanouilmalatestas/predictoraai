#!/bin/bash
set -e

API_URL="https://api.predictoraai.com/health"
MAX_RETRIES=10
SLEEP_BASE=2

echo "[WARZONE++] Pulling latest images..."
docker compose pull

echo "[WARZONE++] Starting deploy..."
docker compose up -d

echo "[WARZONE++] Waiting for backend health..."

attempt=1
success=false

while [[ $attempt -le $MAX_RETRIES ]]; do
    echo "[WARZONE++] Health check attempt $attempt/$MAX_RETRIES..."

    HEALTH=$(curl -s -X GET "$API_URL" || echo "fail")

    if [[ "$HEALTH" == *"ok"* ]]; then
        echo "[WARZONE++] Backend is healthy. Deploy SUCCESS."
        success=true
        break
    fi

    sleep_time=$((SLEEP_BASE ** attempt))
    echo "[WARZONE++] Health not ready. Sleeping $sleep_time seconds..."
    sleep $sleep_time

    attempt=$((attempt + 1))
done

if [[ "$success" = false ]]; then
    echo "[WARZONE++] Deploy FAILED after $MAX_RETRIES attempts. Rolling back..."
    docker compose down
    docker compose up -d
    echo "[WARZONE++] Rollback complete."
fi
