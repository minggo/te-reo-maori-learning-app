# #!/bin/bash

set -euo pipefail

# Ensure mongo is running
docker-compose up -d mongo

# Then start (or restart) fastapi
docker-compose up -d fastapi
