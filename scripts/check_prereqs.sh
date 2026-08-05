#!/usr/bin/env bash
set -euo pipefail

echo "Checking repo prerequisites..."

if command -v ngrok >/dev/null 2>&1; then
  echo "✅ ngrok is installed"
else
  echo "❌ ngrok is not installed"
  echo "   Install it from https://ngrok.com/download"
fi

if [ -d ".venv" ] && [ -f ".venv/bin/activate" ]; then
  echo "✅ .venv exists"
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
