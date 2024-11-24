#!/bin/bash

if [[ "${1}" == "celery" ]]; then
  apt update
  apt install -y postgresql postgresql-contrib
  celery -A services.celery_src.celery_app worker --beat --loglevel=info
elif [[ "${1}" == "flower" ]]; then
  celery -A services.celery_src.celery_app flower
elif [[ "${1}" == "app" ]]; then
  python manage.py collectstatic
  python manage.py makemigrations
  python manage.py migrate

  gunicorn website.wsgi:application --bind=0.0.0.0:8000
  gunicorn main:app --reload --workers=4 --worker-class=uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
 fi