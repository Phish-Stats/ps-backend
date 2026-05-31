#!/usr/bin/env bash
# Drop the entire schema, recreate it, and reseed.
# Usage: ./scripts/reset.sh

set -euo pipefail

COMPOSE_FILE="$(cd "$(dirname "$0")/.." && pwd)/docker-compose.yaml"

echo "⚠️  This will drop all tables and reseed. Press Ctrl+C to cancel."
sleep 3

echo "⬇️  Dropping schema..."
docker compose -f "$COMPOSE_FILE" exec backend alembic downgrade base

echo "⬆️  Recreating schema..."
docker compose -f "$COMPOSE_FILE" exec backend alembic upgrade head

echo "🌱 Seeding..."
docker compose -f "$COMPOSE_FILE" exec backend python -m scripts.seed_db

echo "✅ Reset complete."
