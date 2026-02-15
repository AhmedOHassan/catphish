#!/usr/bin/env bash
# start.sh — Launch both the FastAPI backend and the Vite dev frontend
# Usage:  cd catphish-api && bash start.sh

set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "╔══════════════════════════════════════════╗"
echo "║     Catphish Voice Verification          ║"
echo "╚══════════════════════════════════════════╝"

# ── 1. Check Valkey / Redis ──
echo ""
echo "▶ Checking Valkey / Redis on localhost:6379..."
if command -v redis-cli &>/dev/null; then
  if redis-cli ping 2>/dev/null | grep -q PONG; then
    echo "  ✓ Valkey is running"
  else
    echo "  ✗ Valkey not responding. Start with:  docker compose up -d"
    exit 1
  fi
else
  echo "  ⚠ redis-cli not found; skipping check (make sure Valkey is running)"
fi

# ── 2. Start FastAPI backend ──
echo ""
echo "▶ Starting FastAPI backend on http://localhost:8000 ..."
cd "$ROOT_DIR/server"
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "  Backend PID: $BACKEND_PID"

# ── 3. Start Vite dev server ──
echo ""
echo "▶ Starting Vite frontend on http://localhost:3001 ..."
cd "$ROOT_DIR"
npm run dev &
FRONTEND_PID=$!
echo "  Frontend PID: $FRONTEND_PID"

echo ""
echo "═══════════════════════════════════════════"
echo "  Backend  → http://localhost:8000"
echo "  Frontend → http://localhost:3001"
echo "  Health   → http://localhost:8000/health"
echo "═══════════════════════════════════════════"
echo ""
echo "Press Ctrl+C to stop both servers."

# ── Cleanup on exit ──
cleanup() {
  echo ""
  echo "Shutting down..."
  kill $BACKEND_PID 2>/dev/null || true
  kill $FRONTEND_PID 2>/dev/null || true
  exit 0
}
trap cleanup SIGINT SIGTERM

wait
