#!/usr/bin/env bash
set -euo pipefail

echo "Checking repo prerequisites..."

if command -v ngrok >/dev/null 2>&1; then
  echo "✅ ngrok is installed globally"
elif [ -x "./ngrok" ]; then
  echo "✅ local ngrok binary found at ./ngrok"
else
  echo "⚠️ ngrok is not installed"
  echo "   A local ngrok binary is optional if pyngrok is installed in .venv."
fi

if [ -d ".venv" ] && [ -f ".venv/bin/activate" ]; then
  echo "✅ .venv exists"
  if ./.venv/bin/python -c "import importlib.util; importlib.util.find_spec('pyngrok')" >/dev/null 2>&1; then
    echo "✅ pyngrok is installed in .venv"
  else
    echo "⚠️ pyngrok is not installed in .venv"
    echo "   Install it with: .venv/bin/python -m pip install pyngrok"
  fi
else
  echo "❌ .venv is missing"
  echo "   Create it with: python3 -m venv .venv"
  echo "   Then install requirements: .venv/bin/python -m pip install -r requirements.txt"
fi

if [ -f "backend/token_service.py" ]; then
  echo "✅ backend/token_service.py exists"
else
  echo "❌ backend/token_service.py is missing"
fi

exit 0
