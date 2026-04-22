#!/bin/sh
set -e

case "${1:-migrate-and-start}" in
  migrate)
    echo "[entrypoint] Running migrations..."
    exec alembic upgrade head
    ;;
  start)
    echo "[entrypoint] Starting application..."
    exec gunicorn app.main:app --config gunicorn.conf.py
    ;;
  migrate-and-start)
    echo "[entrypoint] Running migrations..."
    alembic upgrade head
    echo "[entrypoint] Starting application..."
    exec gunicorn app.main:app --config gunicorn.conf.py
    ;;
  *)
    echo "[entrypoint] Unknown command: $1"
    exit 1
    ;;
esac
