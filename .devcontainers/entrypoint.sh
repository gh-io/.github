#!/bin/bash
set -e

echo "Pulling KUBU Docker image..."
docker pull ghcr.io/web4application/kubu:main
echo "KUBU image pulled successfully!"

# Keep container running
exec "$@"
