#!/usr/bin/env bash
set -e

API_KEY="${API_KEY:-demo_key_123}"
TENANT_ID="${TENANT_ID:-t_demo}"

docker exec -i catphish-valkey valkey-cli <<EOF
HSET tenant:by_api_key:${API_KEY} tenant_id "${TENANT_ID}" name "Demo Bank" created_at "2026-02-14T00:00:00Z"
HSET user:${TENANT_ID}:user_001 voice_embedding "[0.1,0.2,0.3]" created_at "2026-02-14T00:00:00Z"
SADD tenant_users:${TENANT_ID} user_001
EOF

echo "Seeded tenant + user into Valkey."

