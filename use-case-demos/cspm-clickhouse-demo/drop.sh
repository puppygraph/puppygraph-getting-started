#!/usr/bin/env bash
# Drops the cspm database so load.sh can recreate it from scratch.
#
# Usage:  ./drop.sh
set -euo pipefail

SERVICE="${CLICKHOUSE_SERVICE:-clickhouse}"
DB="cspm"

ch() { docker compose exec -T "$SERVICE" clickhouse-client "$@"; }

ch --query="DROP DATABASE IF EXISTS $DB SYNC"
echo "Dropped database $DB."
