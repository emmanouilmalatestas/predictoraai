#!/bin/bash
source /etc/environment
set -e

API_HEALTH_URL="https://api.predictoraai.com/health"
CHECK_INTERVAL=30

CONTAINERS=(
  "predictora-backend"
  "predictora-frontend"
  "traefik"
  "predictoraai-db"
  "prometheus"
  "alertmanager"
  "grafana"
)

TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID}"

LOG_DIR="/home/deploy/predictoraai/warzone-logs"
LOG_FILE="$LOG_DIR/guardian.log"
METRICS_FILE="/home/deploy/predictoraai/warzone-metrics/guardian.prom"
MAX_LOG_SIZE=$((5 * 1024 * 1024))

mkdir -p "$LOG_DIR"

log() {
  local msg="[$(date -Iseconds)] $1"
  echo "$msg" | tee -a "$LOG_FILE"
}

rotate_logs_if_needed() {
  if [[ -f "$LOG_FILE" ]]; then
    local size
    size=$(stat -c%s "$LOG_FILE")
    if (( size > MAX_LOG_SIZE )); then
      mv "$LOG_FILE" "$LOG_FILE.$(date +%Y%m%d%H%M%S)"
      touch "$LOG_FILE"
      log "LOG ROTATION: Rotated guardian.log due to size > 5MB"
    fi
  fi
}

telegram_notify() {
  local text="$1"
  if [[ -z "$TELEGRAM_BOT_TOKEN" || -z "$TELEGRAM_CHAT_ID" ]]; then
    log "TELEGRAM: Skipping (no token/chat id configured)"
    return
  fi

  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=${text}" \
    -d "parse_mode=Markdown" >/dev/null 2>&1 || \
    log "TELEGRAM: Failed to send message"
}

check_container() {
  local name="$1"
  local status
  status=$(docker inspect -f '{{.State.Running}}' "$name" 2>/dev/null || echo "false")

  if [[ "$status" != "true" ]]; then
    log "MONITOR: Container $name is DOWN. Attempting restart..."
    telegram_notify "⚠️ *WARZONE MONITOR*: Container \`$name\` is DOWN. Restarting..."

    docker restart "$name" >/dev/null 2>&1 && \
      log "MONITOR: Container $name restarted successfully." && \
      telegram_notify "✅ *WARZONE MONITOR*: Container \`$name\` restarted successfully." || \
      (log "MONITOR: FAILED to restart $name." && \
       telegram_notify "❌ *WARZONE MONITOR*: FAILED to restart container \`$name\`.")
  fi
}

check_backend_health() {
  health=$(curl -s -X GET "$API_HEALTH_URL" || echo "fail")

  if [[ "$health" == *"ok"* ]]; then
    log "WATCHDOG: Backend health OK."
    backend_status=1
  else
    log "WATCHDOG: Backend health FAILED. Response: $health"
    backend_status=0
    telegram_notify "❌ *WARZONE WATCHDOG*: Backend health FAILED.\nResponse: \`$health\`"
  fi
}

write_metrics() {
  echo "# HELP warzone_backend_health Backend health status (1=ok,0=fail)" > $METRICS_FILE
  echo "# TYPE warzone_backend_health gauge" >> $METRICS_FILE
  echo "warzone_backend_health $backend_status" >> $METRICS_FILE

  echo "# HELP warzone_containers_running Number of running containers" >> $METRICS_FILE
  echo "# TYPE warzone_containers_running gauge" >> $METRICS_FILE
  echo "warzone_containers_running $(docker ps -q | wc -l)" >> $METRICS_FILE
}

log "WARZONE GUARDIAN started."

while true; do
  rotate_logs_if_needed

  for c in "${CONTAINERS[@]}"; do
    check_container "$c"
  done

  check_backend_health
  write_metrics

  sleep "$CHECK_INTERVAL"
done
