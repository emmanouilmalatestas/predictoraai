#!/bin/bash
set -e

echo "🚀 Ensuring Grafana provisioning & dashboards..."

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PROV_DIR="$BASE_DIR/grafana/provisioning"
DS_DIR="$PROV_DIR/datasources"
DB_DIR="$PROV_DIR/dashboards"

mkdir -p "$DS_DIR" "$DB_DIR"

echo "📡 Writing datasource.yml..."
cat > "$DS_DIR/datasource.yml" <<EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

echo "📁 Writing dashboards.yml..."
cat > "$DB_DIR/dashboards.yml" <<EOF
apiVersion: 1

providers:
  - name: "predictoraai-dashboards"
    orgId: 1
    folder: "PredictoraAI"
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF

echo "📊 Writing backend.json..."
cat > "$DB_DIR/backend.json" <<'EOF'
{
  "title": "PredictoraAI Backend",
  "uid": "predictora-backend",
  "schemaVersion": 36,
  "version": 1,
  "panels": [
    {
      "type": "stat",
      "title": "Requests per Second",
      "targets": [
        { "expr": "sum(rate(backend_requests_total[1m]))" }
      ]
    },
    {
      "type": "stat",
      "title": "Error Rate (5xx)",
      "targets": [
        { "expr": "sum(rate(backend_request_errors_total[1m]))" }
      ]
    },
    {
      "type": "graph",
      "title": "Latency p95",
      "targets": [
        { "expr": "histogram_quantile(0.95, sum(rate(backend_request_duration_seconds_bucket[5m])) by (le))" }
      ]
    },
    {
      "type": "graph",
      "title": "Latency p99",
      "targets": [
        { "expr": "histogram_quantile(0.99, sum(rate(backend_request_duration_seconds_bucket[5m])) by (le))" }
      ]
    },
    {
      "type": "graph",
      "title": "CPU Usage",
      "targets": [
        { "expr": "rate(container_cpu_usage_seconds_total{container=\"predictora-backend\"}[1m])" }
      ]
    },
    {
      "type": "graph",
      "title": "Memory Usage",
      "targets": [
        { "expr": "container_memory_usage_bytes{container=\"predictora-backend\"}" }
      ]
    }
  ]
}
EOF

echo "📊 Writing traefik.json..."
cat > "$DB_DIR/traefik.json" <<'EOF'
{
  "title": "Traefik Metrics",
  "uid": "predictora-traefik",
  "schemaVersion": 36,
  "version": 1,
  "panels": [
    {
      "type": "graph",
      "title": "Requests by Status Code",
      "targets": [
        { "expr": "sum(rate(traefik_service_requests_total[1m])) by (code)" }
      ]
    },
    {
      "type": "graph",
      "title": "Request Duration p95",
      "targets": [
        { "expr": "histogram_quantile(0.95, sum(rate(traefik_service_request_duration_seconds_bucket[5m])) by (le))" }
      ]
    },
    {
      "type": "graph",
      "title": "Entrypoint Traffic",
      "targets": [
        { "expr": "sum(rate(traefik_entrypoint_requests_total[1m])) by (entrypoint)" }
      ]
    },
    {
      "type": "graph",
      "title": "Router Traffic",
      "targets": [
        { "expr": "sum(rate(traefik_router_requests_total[1m])) by (router)" }
      ]
    },
    {
      "type": "stat",
      "title": "TLS Certificate Expiry (days)",
      "targets": [
        { "expr": "(traefik_tls_certs_not_after - time()) / 86400" }
      ]
    }
  ]
}
EOF

echo "📊 Writing system.json..."
cat > "$DB_DIR/system.json" <<'EOF'
{
  "title": "System Health",
  "uid": "predictora-system",
  "schemaVersion": 36,
  "version": 1,
  "panels": [
    {
      "type": "graph",
      "title": "CPU Usage",
      "targets": [
        { "expr": "100 - (avg by(instance)(rate(node_cpu_seconds_total{mode=\"idle\"}[1m])) * 100)" }
      ]
    },
    {
      "type": "graph",
      "title": "Memory Usage",
      "targets": [
        { "expr": "node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes" }
      ]
    },
    {
      "type": "graph",
      "title": "Disk Usage",
      "targets": [
        { "expr": "node_filesystem_size_bytes - node_filesystem_free_bytes" }
      ]
    },
    {
      "type": "graph",
      "title": "Network Traffic",
      "targets": [
        { "expr": "rate(node_network_receive_bytes_total[1m])" },
        { "expr": "rate(node_network_transmit_bytes_total[1m])" }
      ]
    }
  ]
}
EOF

echo "📊 Writing prometheus.json..."
cat > "$DB_DIR/prometheus.json" <<'EOF'
{
  "title": "Prometheus Overview",
  "uid": "predictora-prometheus",
  "schemaVersion": 36,
  "version": 1,
  "panels": [
    {
      "type": "graph",
      "title": "Scrape Duration",
      "targets": [
        { "expr": "rate(prometheus_target_scrapes_exceeded_sample_limit_total[1m])" }
      ]
    },
    {
      "type": "graph",
      "title": "Active Targets",
      "targets": [
        { "expr": "count(up)" }
      ]
    },
    {
      "type": "graph",
      "title": "TSDB Head Chunks",
      "targets": [
        { "expr": "prometheus_tsdb_head_chunks" }
      ]
    },
    {
      "type": "graph",
      "title": "Prometheus CPU",
      "targets": [
        { "expr": "rate(process_cpu_seconds_total[1m])" }
      ]
    }
  ]
}
EOF

echo "🔄 Restarting Grafana..."
docker rm -f grafana >/dev/null 2>&1 || true
docker compose up -d grafana

echo "✅ Grafana dashboards & datasource ensured."
