#!/bin/bash

if [[ "${1}" == "celery" ]]; then
  echo "Starting Celery worker..."
  celery -A website worker  --loglevel=info
elif [[ "${1}" == "celery-beat" ]]; then
  echo "Starting Celery beat..."
  celery -A website beat --loglevel=info
elif [[ "${1}" == "flower" ]]; then
  echo "Starting Flower..."
  celery -A website.celery.app flower --broker=redis://${REDIS_HOST}:${REDIS_PORT}/${REDIS_DB} --basic_auth=${FLOWER_USER}:${FLOWER_PASS}
elif [[ "${1}" == "app" ]]; then
  echo "Running Django setup tasks..."
  python manage.py collectstatic --noinput
  python manage.py makemigrations
  python manage.py migrate

  echo "Creating superuser..."
  python manage.py shell << EOF
from django.contrib.auth import get_user_model
from django.core.management import call_command

User = get_user_model()
if not User.objects.filter(email="${DJANGO_SUPERUSER_EMAIL}").exists():
    User.objects.create_superuser(
        email="${DJANGO_SUPERUSER_EMAIL}",
        password="${DJANGO_SUPERUSER_PASSWORD}",
        login="${DJANGO_SUPERUSER_LOGIN}"
    )
EOF
  echo "Superuser ${DJANGO_SUPERUSER_LOGIN} is created..."

  gunicorn --config ./config/gunicorn.conf.py website.wsgi:application
 fi