#!/bin/bash

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

  gunicorn --config ./config/gunicorn.conf.py website.wsgi:application
 fi