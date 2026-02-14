# catphish

## Quickstart (Valkey)

## One-command setup

```bash
./scripts/setup.sh
```

## To run Valkey locally only

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
