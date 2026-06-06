#!/bin/bash
set -e

echo "📡 Installing Grafana datasource provisioning..."

mkdir -p ./grafana/provisioning/datasources

cat > ./grafana/provisioning/datasources/datasource.yml <<EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

echo "🔄 Restarting Grafana to apply provisioning..."
docker rm -f grafana
docker compose up -d grafana

echo "✅ Grafana datasource installed."
