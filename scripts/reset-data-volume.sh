#!/usr/bin/env sh

set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

cd "$ROOT_DIR"

echo "Stopping backend stack and removing the data volume..."
docker compose down -v --remove-orphans

echo "Removing local SQLite leftovers if they exist..."
rm -f instance/*.db

echo "Done."
