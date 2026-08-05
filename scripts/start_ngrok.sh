#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ ! -d ".venv" ] || [ ! -f ".venv/bin/activate" ]; then
  echo "Error: .venv not found. Create the venv first with './.venv/bin/python -m venv .venv' and install requirements."
  exit 1
fi

if ! command -v ngrok >/dev/null 2>&1; then
  echo "Error: ngrok is not installed. Install it from https://ngrok.com/download"
  exit 1
fi

if [ -f "backend/token_service.py" ]; then
  echo "Starting backend server..."
  ./.venv/bin/python backend/token_service.py &
  BACKEND_PID=$!
else
  echo "Error: backend/token_service.py not found."
  exit 1
fi

cleanup() {
  printf "\nStopping backend (pid %s)...\n" "$BACKEND_PID"
  kill "$BACKEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Waiting for backend to initialize..."
sleep 2

echo "Starting ngrok on port 5000..."
ngrok http 5000

# ngrok runs in foreground; when it exits the trap will stop the backend.
