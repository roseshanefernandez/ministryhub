#!/bin/sh
set -e

echo "Waiting for Database..."

until python manage.py shell -c "
from django.db import connection
connection.ensure_connection()
"; do
    sleep 5
done

echo "Database ready"

# Run database setup steps
python manage.py migrate
python manage.py collectstatic --noinput

# CHECK: If a custom command was passed to Docker (e.g., from compose.yaml), execute it.
if [ $# -gt 0 ]; then
    echo "Running custom command: $@"
    exec "$@"
else
    # Default fallback: Production Gunicorn server
    echo "Starting Gunicorn production server..."
    exec gunicorn core.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 3
fi
