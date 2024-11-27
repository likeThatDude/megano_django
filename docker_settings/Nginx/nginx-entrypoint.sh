#!/bin/sh
set -e

# Подставляем переменные окружения в конфигурацию nginx
envsubst '${CONTAINER_APP_NAME},${SERVER_DOMAIN}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Запускаем nginx
exec "$@"