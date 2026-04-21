#!/bin/sh
set -e

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting application..."
exec gunicorn app.main:app --config gunicorn.conf.py
