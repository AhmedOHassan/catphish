#!/usr/bin/env bash
set -euo pipefail

# Start Valkey
docker compose up -d 2>/dev/null || docker-compose up -d

# Seed demo keys
chmod +x ./scripts/seed-valkey.sh
./scripts/seed-valkey.sh

echo "✅ Valkey is up and seeded."
echo "Run: docker exec -it catphish-valkey valkey-cli PING"

