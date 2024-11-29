FROM edoburu/pgbouncer:latest

USER root

# Установка необходимых утилит
RUN apk add --no-cache postgresql-client && \
    adduser -D -H -h /etc/pgbouncer pgbouncer

# Копирование конфигурационных файлов
COPY init-pgbouncer.sh /etc/pgbouncer/init-pgbouncer.sh

# Установка прав на выполнение и владельца
RUN chmod +x /etc/pgbouncer/init-pgbouncer.sh && \
    chown -R pgbouncer:pgbouncer /etc/pgbouncer

# Создание директории для PID файла и логов
RUN mkdir -p /var/run/pgbouncer /var/log/pgbouncer && \
    chown -R pgbouncer:pgbouncer /var/run/pgbouncer /var/log/pgbouncer && \
    chmod 755 /var/run/pgbouncer /var/log/pgbouncer

USER pgbouncer

ENTRYPOINT ["/bin/sh", "/etc/pgbouncer/init-pgbouncer.sh"]