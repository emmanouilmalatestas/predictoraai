#!/bin/bash
set -e

DOCKER_USER="manolio"
REPO_BACKEND="predictora-backend"
REPO_FRONTEND="predictora-frontend"

echo "[WARZONE] Building backend..."
cd backend
docker build -t $DOCKER_USER/$REPO_BACKEND:latest .

echo "[WARZONE] Building frontend..."
cd ../frontend
docker build -t $DOCKER_USER/$REPO_FRONTEND:latest .

echo "[WARZONE] Pushing backend..."
docker push $DOCKER_USER/$REPO_BACKEND:latest

echo "[WARZONE] Pushing frontend..."
docker push $DOCKER_USER/$REPO_FRONTEND:latest

echo "[WARZONE] Build + Push complete."
