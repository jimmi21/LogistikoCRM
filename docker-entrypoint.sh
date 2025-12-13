#!/bin/bash
# ============================================================================
# D.P. Economy - Docker Entrypoint Script
# ============================================================================

set -e

echo "==========================================="
echo " D.P. Economy - Starting Container"
echo "==========================================="

# Wait for database
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.5
done
echo "✅ Database is ready!"

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 0.5
done
echo "✅ Redis is ready!"

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@dpeconomy.local', 'admin')
    print('✅ Superuser created (username: admin, password: admin)')
else:
    print('✅ Superuser already exists')
EOF

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "==========================================="
echo " ✅ Setup Complete!"
echo "==========================================="

# Execute the main command
exec "$@"
