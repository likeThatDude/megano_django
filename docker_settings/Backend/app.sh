#!/bin/bash

echo "Superuser email: ${DJANGO_SUPERUSER_EMAIL}"
echo "Superuser password: ${DJANGO_SUPERUSER_PASSWORD}"
echo "Superuser login: ${DJANGO_SUPERUSER_LOGIN}"


if [[ "${1}" == "celery" ]]; then
  apt update
  apt install -y postgresql postgresql-contrib
  celery -A services.celery_src.celery_app worker --beat --loglevel=info
elif [[ "${1}" == "flower" ]]; then
  celery -A services.celery_src.celery_app flower
elif [[ "${1}" == "app" ]]; then
  python manage.py collectstatic --noinput
  python manage.py makemigrations
  python manage.py migrate auth
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