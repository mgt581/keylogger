#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ ! -d ".venv" ] || [ ! -f ".venv/bin/activate" ]; then
  echo "Error: .venv not found. Create the venv first with './.venv/bin/python -m venv .venv' and install requirements."
  exit 1
fi

NGROK_CMD=""
USE_PYNGROK=false
PYNGROK_AVAILABLE=false
NGROK_AUTHTOKEN="${NGROK_AUTHTOKEN:-${NGROK_AUTH_TOKEN:-}}"

if ./.venv/bin/python -c "import importlib.util; importlib.util.find_spec('pyngrok')" >/dev/null 2>&1; then
  PYNGROK_AVAILABLE=true
fi

if [ -x "$HOME/Library/Application Support/ngrok/ngrok" ]; then
  NGROK_CMD="$HOME/Library/Application Support/ngrok/ngrok"
elif command -v ngrok >/dev/null 2>&1; then
  NGROK_CMD="ngrok"
elif [ -x "./ngrok" ]; then
  NGROK_CMD="./ngrok"
fi

if [ -n "$NGROK_CMD" ]; then
  NGROK_VERSION=$("$NGROK_CMD" version 2>/dev/null | awk '{print $3}' || true)
  if [ -n "$NGROK_VERSION" ]; then
    NGROK_MAJOR=${NGROK_VERSION%%.*}
    if [ "$NGROK_MAJOR" -lt 3 ]; then
      if [ "$PYNGROK_AVAILABLE" = true ]; then
        echo "Detected ngrok version $NGROK_VERSION, using pyngrok from .venv instead."
        USE_PYNGROK=true
      else
        echo "Warning: detected ngrok version $NGROK_VERSION. Current accounts may require ngrok v3.20.0 or newer."
        echo "If you see ERR_NGROK_121, download a newer ngrok binary from https://ngrok.com/download."
      fi
    fi
  fi
fi

BACKEND_PORT="${BACKEND_PORT:-5000}"

if [ "$USE_PYNGROK" = false ] && [ -z "$NGROK_CMD" ]; then
  if [ "$PYNGROK_AVAILABLE" = true ]; then
    USE_PYNGROK=true
  else
    echo "Error: ngrok is not installed and pyngrok is not available in .venv."
    echo "Install ngrok or run: .venv/bin/python -m pip install pyngrok"
    exit 1
  fi
fi

if [ -f "backend/token_service.py" ]; then
  echo "Starting backend server on port $BACKEND_PORT..."
  BACKEND_PORT_ARG="--port=$BACKEND_PORT"
  ./.venv/bin/python backend/token_service.py $BACKEND_PORT_ARG &
  BACKEND_PID=$!
else
  echo "Error: backend/token_service.py not found."
  exit 1
fi

cleanup() {
  printf "\nStopping backend (pid %s)...\n" "$BACKEND_PID"
  kill "$BACKEND_PID" 2>/dev/null || true
  if [ "$USE_PYNGROK" = true ]; then
    ./.venv/bin/python - <<'PY'
from pyngrok import ngrok
ngrok.disconnect('http://127.0.0.1:4040')
PY
  fi
}
trap cleanup EXIT INT TERM

echo "Waiting for backend to initialize..."
sleep 2

if [ "$USE_PYNGROK" = true ]; then
  echo "Starting tunnel with pyngrok..."
  ./.venv/bin/python - <<'PY'
from pyngrok import conf, ngrok
from time import sleep
import os

ngrok_token = os.getenv('NGROK_AUTHTOKEN') or os.getenv('NGROK_AUTH_TOKEN')
if ngrok_token:
    ngrok.set_auth_token(ngrok_token)
backend_port = int(os.getenv('BACKEND_PORT', '5000'))
public_url = ngrok.connect(backend_port, bind_tls=True).public_url
print('Public URL:', public_url)
sleep(999999)
PY
else
  NGROK_VERSION=$("$NGROK_CMD" version 2>/dev/null | awk '{print $3}')
  if [ -n "$NGROK_VERSION" ]; then
    NGROK_MAJOR=${NGROK_VERSION%%.*}
    if [ "$NGROK_MAJOR" -lt 3 ]; then
      echo "Warning: detected ngrok version $NGROK_VERSION. Current accounts may require ngrok v3.20.0 or newer."
      echo "If you see ERR_NGROK_121, download a newer ngrok binary from https://ngrok.com/download."
    fi
  fi

  echo "Starting ngrok on port $BACKEND_PORT..."
  $NGROK_CMD http "$BACKEND_PORT"
fi

# ngrok runs in foreground; when it exits the trap will stop the backend.
