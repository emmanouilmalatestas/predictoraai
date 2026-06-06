#!/bin/bash

CONTAINER="traefik"
METRICS_URL="http://traefik:8080/metrics"

if ! curl -fsS --max-time 3 "$METRICS_URL" >/dev/null 2>&1; then
  echo "[auto-heal] traefik DOWN, restarting $CONTAINER..."
  docker restart "$CONTAINER"
fi
