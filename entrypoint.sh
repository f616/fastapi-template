#!/bin/sh
# entrypoint.sh

# Wait for MySQL to be available on port 3306
while ! nc -z db 3306; do
  echo "Waiting for MySQL on db:3306..."
  sleep 2
done

echo "MySQL is up - starting the application."
exec uvicorn app.main:app --host 0.0.0.0 --port 80
