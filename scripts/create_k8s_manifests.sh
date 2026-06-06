#!/usr/bin/env bash
set -euo pipefail

mkdir -p k8s

cat > k8s/backend.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: predictora-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: predictora-backend
  template:
    metadata:
      labels:
        app: predictora-backend
    spec:
      containers:
        - name: predictora-backend
          image: docker.io/manolio/predictora-backend:latest
          ports:
            - containerPort: 8000
          envFrom:
            - secretRef:
                name: predictora-backend-secrets
---
apiVersion: v1
kind: Service
metadata:
  name: predictora-backend
spec:
  selector:
    app: predictora-backend
  ports:
    - port: 8000
      targetPort: 8000
EOF

cat > k8s/frontend.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: predictora-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: predictora-frontend
  template:
    metadata:
      labels:
        app: predictora-frontend
    spec:
      containers:
        - name: predictora-frontend
          image: docker.io/manolio/predictora-frontend:latest
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: predictora-frontend
spec:
  selector:
    app: predictora-frontend
  ports:
    - port: 80
      targetPort: 80
EOF

echo "Created k8s/backend.yaml and k8s/frontend.yaml"
