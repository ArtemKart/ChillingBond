#!/bin/sh

set -e

echo "Run load testing..."
echo "======================================"

echo "run Docker Compose..."
docker compose --env-file tests/load/.env.locust -f tests/load/docker-compose.loadtest.yml down -v
docker compose --env-file tests/load/.env.locust -f tests/load/docker-compose.loadtest.yml up -d --build

sleep 5

echo "Run database setup"
uv run python -m tests.load.setup_test_db

echo "Run Locust..."
echo "======================================"
uv run locust -f tests/load/locustfile.py --host=http://localhost:8001
