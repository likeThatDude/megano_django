#!/bin/sh
set -e

# Create pgbouncer.ini dynamically
cat > /etc/pgbouncer/pgbouncer.ini << EOF
[databases]
${DB_NAME} = host=${DB_HOST} port=5432 auth_user=${DB_USER}

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = trust
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
#
## Print the generated configuration
#echo "Generated pgbouncer.ini:"
#echo "========================"
#cat /etc/pgbouncer/pgbouncer.ini
#echo "========================"

# Create userlist.txt with SCRAM-SHA-256 authentication
echo "\"${DB_USER}\" \"${DB_PASSWORD}\"" > /etc/pgbouncer/userlist.txt
# Ensure proper permissions
chmod 600 /etc/pgbouncer/userlist.txt

## Generate SCRAM-SHA-256 hash using pg_verifypass
#echo "Generating SCRAM-SHA-256 hash for user ${DB_USER}"
#DB_PASSWORD_HASH=$(psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} -Atc "SELECT passwd FROM pg_shadow WHERE usename='${DB_USER}'")
#echo "Hash generated successfully"
#echo "\"${DB_USER}\" \"${DB_PASSWORD_HASH}\""

# Wait for PostgreSQL to be ready
until pg_isready -h ${DB_HOST} -p 5432 -U ${DB_USER} -d ${DB_NAME}; do
    echo "Waiting for PostgreSQL to be ready..."
    sleep 2
done
# Start PgBouncer
exec pgbouncer /etc/pgbouncer/pgbouncer.ini