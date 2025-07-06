#!/bin/bash
set -e

echo "Starting D&D Campaign Builder with LiteFS..."

# Set default environment variables
export DJANGO_DEBUG=${DJANGO_DEBUG:-"false"}
export PRIMARY_REGION=${PRIMARY_REGION:-"lhr"}

# Function to wait for LiteFS to be ready
wait_for_litefs() {
    echo "Waiting for LiteFS to be ready..."
    while [ ! -f "$LITEFS_DIR/.litefs/db" ]; do
        echo "LiteFS not ready yet, waiting..."
        sleep 1
    done
    echo "LiteFS is ready!"
}

# Function to run Django management commands
run_django_commands() {
    echo "Running Django management commands..."
    
    # Collect static files
    echo "Collecting static files..."
    python manage.py collectstatic --noinput --clear
    
    # Run database migrations
    echo "Running database migrations..."
    python manage.py migrate --noinput
    
    # Create superuser if specified
    if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
        echo "Creating superuser..."
        python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created.')
else:
    print('Superuser already exists.')
EOF
    fi
}

# Function to start the Django application
start_django() {
    echo "Starting Django application with Gunicorn..."
    exec gunicorn \
        --bind "0.0.0.0:8000" \
        --workers 2 \
        --worker-class gthread \
        --worker-connections 1000 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --timeout 30 \
        --keep-alive 2 \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        dnd_companion.wsgi:application
}

# Check if we're running LiteFS mount
if [ "$1" = "litefs" ] && [ "$2" = "mount" ]; then
    # This is the primary LiteFS process
    echo "Starting LiteFS mount..."
    
    # Start LiteFS in the background
    exec litefs mount -config /etc/litefs.yml &
    LITEFS_PID=$!
    
    # Wait for LiteFS to be ready
    wait_for_litefs
    
    # Run Django commands only on the primary node
    if [ "${FLY_REGION}" = "${PRIMARY_REGION}" ]; then
        echo "Running on primary region, executing Django setup..."
        run_django_commands
    else
        echo "Running on replica region, skipping Django setup..."
    fi
    
    # Start Django application
    start_django
    
elif [ "$1" = "django" ]; then
    # Direct Django start (for development or testing)
    echo "Starting Django directly..."
    run_django_commands
    start_django
    
elif [ "$1" = "manage.py" ]; then
    # Run Django management commands
    shift
    exec python manage.py "$@"
    
elif [ "$1" = "shell" ] || [ "$1" = "bash" ]; then
    # Interactive shell
    exec bash
    
else
    # Default: run the command as-is
    exec "$@"
fi