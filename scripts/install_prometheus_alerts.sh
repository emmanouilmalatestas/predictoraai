#!/bin/bash
set -e

echo "🚀 Installing Prometheus alert rules..."

ALERT_FILE="./prometheus/alert.rules.yml"

mkdir -p ./prometheus

cat > $ALERT_FILE <<EOF
groups:
  - name: predictoraai-alerts
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

      - alert: PrometheusDown
        expr: up{job="prometheus"} == 0
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
docker exec prometheus kill -HUP 1

echo "✅ Prometheus alerts installed."
