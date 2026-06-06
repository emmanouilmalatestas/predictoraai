#!/bin/bash

echo "=== PredictoraAI Monitoring Doctor ==="

check() {
  NAME="$1"
  CMD="$2"
  FIX="$3"

  echo -n "[CHECK] $NAME ... "

  if eval "$CMD" >/dev/null 2>&1; then
    echo "OK"
  else
    echo "FAIL"
    if [ -n "$FIX" ]; then
      echo "       -> Fixing: $FIX"
      eval "$FIX"
    fi
  fi
}

# ----------------------------------------
# BACKEND HEALTH
# ----------------------------------------
check "Backend health" \
  "curl -fsS --max-time 3 http://predictora-backend:8000/health" \
  "docker restart predictora-backend"

# ----------------------------------------
# TRAEFIK HEALTH
# ----------------------------------------
check "Traefik metrics" \
  "curl -fsS --max-time 3 http://traefik:8080/metrics" \
  "docker restart traefik"

# ----------------------------------------
# PROMETHEUS HEALTH
# ----------------------------------------
check "Prometheus API" \
  "curl -fsS --max-time 3 http://prometheus:9090/-/ready" \
  "docker restart prometheus"

# ----------------------------------------
# ALERTMANAGER HEALTH
# ----------------------------------------
check "Alertmanager API" \
  "curl -fsS --max-time 3 http://alertmanager:9093/-/ready" \
  "docker restart alertmanager"

# ----------------------------------------
# GRAFANA HEALTH
# ----------------------------------------
check "Grafana API" \
  "curl -fsS --max-time 3 http://grafana:3000/api/health" \
  "docker restart grafana"

# ----------------------------------------
# NODE HEALTH (CPU, RAM, DISK)
# ----------------------------------------
CPU=$(awk -v FS=" " '/cpu /{print ($2+$4)*100/($2+$4+$5)}' /proc/stat | cut -d. -f1)
RAM=$(free | awk '/Mem/{printf("%.0f"), $3/$2 * 100}')
DISK=$(df / | awk 'NR==2{print $5}' | tr -d '%')

echo "[CHECK] Node CPU usage: $CPU%"
echo "[CHECK] Node RAM usage: $RAM%"
echo "[CHECK] Node Disk usage: $DISK%"

if [ "$CPU" -gt 90 ]; then
  echo "       WARNING: CPU > 90%"
fi

if [ "$RAM" -gt 90 ]; then
  echo "       WARNING: RAM > 90%"
fi

if [ "$DISK" -gt 90 ]; then
  echo "       WARNING: DISK > 90%"
fi

echo "=== Monitoring Doctor Completed ==="
