#!/usr/bin/env bash
# Seed the database with albums and songs.
# Usage: ./scripts/seed.sh

set -euo pipefail

COMPOSE_FILE="$(cd "$(dirname "$0")/.." && pwd)/docker-compose.yaml"

echo "🌱 Seeding database..."
docker compose -f "$COMPOSE_FILE" exec backend python -m scripts.seed_db
echo "✅ Done."
