#!/bin/bash
set -e

PROJECT_DIR="/home/deploy/predictoraai"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"

cd "$PROJECT_DIR"

echo "[WARZONE] Adding Traefik middlewares for security..."

# 1) Create dynamic config file for middlewares
mkdir -p traefik/dynamic

cat > traefik/dynamic/security.yml << 'EOF'
http:
  middlewares:
    api-rate-limit:
      rateLimit:
        average: 60
        burst: 120

    strip-bad-paths:
      redirectRegex:
        regex: ".*(wp-admin|wp-login|phpmyadmin|xmlrpc.php).*"
        replacement: "/"
        permanent: true
EOF

echo "[WARZONE] Ensure Traefik loads dynamic config..."

if ! grep -q "traefik/dynamic" "$COMPOSE_FILE"; then
  echo "[WARZONE] You must ensure traefik service has:"
  echo "  - ./traefik/dynamic:/etc/traefik/dynamic"
  echo "and in traefik static config:"
  echo "  providers.file.directory=/etc/traefik/dynamic"
  echo "  providers.file.watch=true"
else
  echo "[WARZONE] Dynamic config volume already referenced in compose."
fi

echo "[WARZONE] Remember to attach middlewares to api router, e.g.:"
echo '  - "traefik.http.routers.api.middlewares=api-rate-limit@file,strip-bad-paths@file"'

echo "[WARZONE] Security baseline written."
