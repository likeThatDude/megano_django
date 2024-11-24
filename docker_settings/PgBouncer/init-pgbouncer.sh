#!/bin/sh
set -e

# Create pgbouncer.ini dynamically
cat > /etc/pgbouncer/pgbouncer.ini << EOF
[databases]
${DB_NAME} = host=${DB_HOST} port=5432 auth_user=${DB_USER}

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = ${POOL_MODE}
max_client_conn = ${MAX_CLIENT_CONN}
default_pool_size = ${DEFAULT_POOL_SIZE}
min_pool_size = 10
reserve_pool_size = 5
reserve_pool_timeout = 3
max_db_connections = 50
max_user_connections = 50
server_reset_query = DISCARD ALL
ignore_startup_parameters = extra_float_digits

logfile = /var/log/pgbouncer/pgbouncer.log
pidfile = /var/run/pgbouncer/pgbouncer.pid
admin_users = ${DB_USER}
EOF

# Create userlist.txt with SCRAM-SHA-256 authentication
echo "\"${DB_USER}\" \"${DB_PASSWORD}\"" > /etc/pgbouncer/userlist.txt

# Ensure proper permissions
chmod 600 /etc/pgbouncer/userlist.txt

# Wait for PostgreSQL to be ready
until pg_isready -h ${DB_HOST} -p 5432 -U ${DB_USER}; do
    echo "Waiting for PostgreSQL to be ready..."
    sleep 2
done

# Start PgBouncer
exec pgbouncer /etc/pgbouncer/pgbouncer.ini