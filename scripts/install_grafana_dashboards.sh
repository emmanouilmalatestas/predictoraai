#!/bin/bash
set -e

echo "📊 Installing Grafana dashboards..."

DASH_DIR="./grafana/provisioning/dashboards"
mkdir -p $DASH_DIR

# Backend dashboard placeholder
cat > $DASH_DIR/backend.json <<EOF
{
  "title": "PredictoraAI Backend",
  "panels": []
}
EOF

# Traefik dashboard placeholder
cat > $DASH_DIR/traefik.json <<EOF
{
  "title": "Traefik Metrics",
  "panels": []
}
EOF

# System dashboard placeholder
cat > $DASH_DIR/system.json <<EOF
{
  "title": "System Health",
  "panels": []
}
EOF

# Prometheus dashboard placeholder
cat > $DASH_DIR/prometheus.json <<EOF
{
  "title": "Prometheus Overview",
  "panels": []
}
EOF

# Provisioning file
cat > ./grafana/provisioning/dashboards/dashboards.yml <<EOF
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

echo "🔄 Restarting Grafana..."
docker rm -f grafana
docker compose up -d grafana

echo "✅ Grafana dashboards installed."
