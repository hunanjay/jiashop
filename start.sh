#!/bin/sh

# Wait for database to be ready
echo "Waiting for postgres..."

while ! nc -z db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

# Run migrations
echo "Running migrations..."
python3 -m alembic -c db/alembic.ini upgrade head

# Seed mock data
echo "Seeding mock data..."
python3 seed_mock_data.py

# Start application
echo "Starting application..."
python3 app.py
