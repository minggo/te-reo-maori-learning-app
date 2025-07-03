#!/bin/bash

set -e

source .venv/bin/activate
pip install -r requirements.txt

# Check if port 27017 is already in use
if lsof -iTCP:27017 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "⚠️ Port 27017 is already in use. Skipping docker mongo startup (maybe already running)."
else
  # Stop mongo container if running
  if docker ps --format '{{.Names}}' | grep -Eq '^mongo$'; then
    echo "⏹️ Stopping existing mongo container..."
    docker stop mongo > /dev/null
  fi

  # Remove mongo container if exists
  if docker ps -a --format '{{.Names}}' | grep -Eq '^mongo$'; then
    echo "🗑️ Removing old mongo container..."
    docker rm mongo > /dev/null
  fi

  # Start a fresh mongo container
  echo "🚀 Starting mongo container..."
  docker run -d --name mongo -p 27017:27017 mongo
fi

uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
