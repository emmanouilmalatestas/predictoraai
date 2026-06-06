#!/bin/bash
set -e

echo "🚀 Starting PredictoraAI Monitoring Bootstrap..."

# Load environment
source ./backend/.env

GRAFANA_URL="https://grafana.predictoraai.com"
GRAFANA_TOKEN="$GRAFANA_API_TOKEN"

PROMETHEUS_CONTAINER="prometheus"
GRAFANA_CONTAINER="grafana"

DASHBOARD_DIR="./monitoring/dashboards"
ALERTS_DIR="./monitoring/alerts"

mkdir -p $DASHBOARD_DIR
mkdir -p $ALERTS_DIR

echo "📥 Downloading dashboards..."

curl -s -o $DASHBOARD_DIR/backend.json \
  https://raw.githubusercontent.com/grafana/grafana/main/devenv/dashboards/backend.json

curl -s -o $DASHBOARD_DIR/traefik.json \
  https://raw.githubusercontent.com/traefik/traefik/master/contrib/grafana/traefik.json

curl -s -o $DASHBOARD_DIR/node.json \
  https://raw.githubusercontent.com/prometheus/node_exporter/master/docs/node-mixin/dashboards/node.json

curl -s -o $DASHBOARD_DIR/prometheus.json \
  https://raw.githubusercontent.com/prometheus/prometheus/main/documentation/prometheus-mixin/dashboards/prometheus.json

echo "📊 Importing dashboards into Grafana..."

for file in $DASHBOARD_DIR/*.json; do
  echo "➡ Importing $file"
  curl -s -X POST "$GRAFANA_URL/api/dashboards/db" \
    -H "Authorization: Bearer $GRAFANA_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"dashboard\": $(cat $file), \"overwrite\": true}"
done

echo "⚠️ Installing alert rules..."

cat > $ALERTS_DIR/predictora-alerts.yml <<EOF
groups:
- name: predictora-alerts
  rules:
  - alert: BackendDown
    expr: up{job="backend"} == 0
    for: 1m
    labels:
      severity: critical
  - alert: TraefikDown
    expr: up{job="traefik"} == 0
    for: 1m
    labels:
      severity: critical
  - alert: BackendHighLatency
    expr: histogram_quantile(0.95, sum(rate(backend_request_duration_seconds_bucket[5m])) by (le)) > 0.5
    for: 5m
    labels:
      severity: warning
  - alert: BackendHighErrorRate
    expr: sum(rate(backend_request_errors_total[5m])) / sum(rate(backend_requests_total[5m])) > 0.05
    for: 5m
    labels:
      severity: critical
EOF

echo "🔄 Reloading Prometheus..."

docker exec $PROMETHEUS_CONTAINER kill -HUP 1

echo "🔍 Checking target health..."

sleep 3

docker exec $PROMETHEUS_CONTAINER wget -qO- http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

echo "🎉 Monitoring bootstrap complete!"
