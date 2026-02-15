# catphish

## Make sure you have a .env

## python -m venv .venv

## pip install -r requirements.txt

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

## Test the backend

## 1) Start the backend
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## 2) Check health
```bash
curl http://127.0.0.1:8000/health
```

## 3) Manual curl test

### 3A) Enroll

```bash
curl -s -X POST http://127.0.0.1:8000/v1/enroll \
  -H "Content-Type: application/json" \
  -H "X-Catphish-Key: demo_key_123" \
  -d '{"external_user_id":"user_001","audio_sample":"AAAA...fakebase64...BBBB","metadata":{"reason":"demo"}}' | jq
```

### 3B) Create Challenge
```bash
curl -s -X POST http://127.0.0.1:8000/v1/challenges \
  -H "Content-Type: application/json" \
  -H "X-Catphish-Key: demo_key_123" \
  -d '{"external_user_id":"user_001","purpose":"login","ttl_seconds":120}' | jq
```

### 3C) Verify Challenge

Fill in challenge id

```bash
curl -s -X POST http://127.0.0.1:8000/v1/challenges/ch_XXXXXXXX/verify \
  -H "Content-Type: application/json" \
  -H "X-Catphish-Key: demo_key_123" \
  -d '{"external_user_id":"user_001","audio_sample":"AAAA...fakebase64...BBBB"}' | jq
```
