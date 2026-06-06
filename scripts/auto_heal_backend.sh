#!/bin/bash

CONTAINER="predictora-backend"
HEALTH_URL="http://predictora-backend:8000/health"

if ! curl -fsS --max-time 3 "$HEALTH_URL" >/dev/null 2>&1; then
  echo "[auto-heal] backend DOWN, restarting $CONTAINER..."
  docker restart "$CONTAINER"
fi
