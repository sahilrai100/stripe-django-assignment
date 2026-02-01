#!/bin/sh
set -e

# Wait for DB to be ready
echo "Waiting for database..."
while ! python - <<'PY'
import sys
import os
import socket
from urllib.parse import urlparse
url = os.environ.get('DATABASE_URL')
if not url:
    sys.exit(0)

# crude check for postgres
parsed = urlparse(url)
host = parsed.hostname or 'db'
port = parsed.port or 5432
s = socket.socket()
try:
    s.connect((host, port))
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
do
  sleep 1
done

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Create superuser if env provided
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Creating superuser (if missing)..."
  python - <<'PY'
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
if username and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print('Superuser created')
    else:
        print('Superuser already exists')
else:
    print('Superuser env vars not set')
PY
fi

# Collect static (optional)
python manage.py collectstatic --noinput || true

# Exec what was passed (e.g., gunicorn)
exec "$@"
