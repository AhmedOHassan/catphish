# catphish

## Quickstart (Valkey)

## 1) Start Valkey
```bash
docker compose up -d
```

## 2) Seed demo data
```bash
./scripts/seed-valkey.sh
```

## 3) Verify
```bash
docker exec -it catphish-valkey valkey-cli PING
docker exec -it catphish-valkey valkey-cli HGETALL tenant:by_api_key:demo_key_123
```
