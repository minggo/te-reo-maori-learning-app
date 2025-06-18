#!/bin/bash

source .venv/bin/activate
pip install -r requirements.txt

if ! docker ps -a --format '{{.Names}}' | grep -Eq '^mongo$'; then
  docker run -d --name mongo -p 27017:27017 mongo
else
  echo "✅ Mongo container already exists."
  docker start mongo > /dev/null
fi

uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
