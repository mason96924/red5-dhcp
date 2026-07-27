#!/usr/bin/env bash
# Run the Red5-DHCP BMS supervisory service.
#   ./run.sh            -> http://127.0.0.1:8020
#   PORT=9000 ./run.sh  -> custom port
set -euo pipefail
cd "$(dirname "$0")"

PORT="${PORT:-8020}"
PY=".venv/bin/python"
[ -x "$PY" ] || PY="python3"

exec "$PY" -m uvicorn backend.server:app --host 0.0.0.0 --port "$PORT" "$@"
