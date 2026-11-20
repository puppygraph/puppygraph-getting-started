#!/usr/bin/env bash
# One-shot run of the PuppyGraph analyst: ./run.sh "your question"
# Without an argument, opens the interactive Omnigent REPL.
set -euo pipefail
cd "$(dirname "$0")"
[ -f .env ] || cp .env.example .env
set -a; . ./.env; set +a
if grep -qF '${OPENAI_API_KEY}' agent/config.yaml; then
  : "${OPENAI_API_KEY:?set OPENAI_API_KEY (in .env or the environment)}"
fi
command -v puppygraph-mcp >/dev/null || { echo "puppygraph-mcp not on PATH; see README" >&2; exit 1; }
if [ $# -gt 0 ]; then
  exec omnigent run agent/ --no-session -p "$*"
else
  exec omnigent run agent/
fi
