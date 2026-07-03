#!/usr/bin/env bash
# Launch the Standardized CIP Database Validation tool.
# Stops any process already on port 5050, opens the browser, then runs Flask.

set -e
cd "$(dirname "$0")"

PORT=5050
URL="http://localhost:${PORT}"

# Free port 5050 if anything is bound to it
EXISTING_PID="$(lsof -ti:${PORT} 2>/dev/null || true)"
if [ -n "${EXISTING_PID}" ]; then
  echo "Stopping existing process on port ${PORT} (pid ${EXISTING_PID})"
  kill -9 ${EXISTING_PID} 2>/dev/null || true
  sleep 1
fi

# Open the browser shortly after Flask boots (runs in the background)
( sleep 2; open "${URL}" ) &

# Pick the first available python
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Error: no python interpreter found in PATH"
  exit 1
fi

echo "Starting CIP Validation Tool at ${URL}"
echo "Press Ctrl+C to stop."
exec "${PY}" app.py
