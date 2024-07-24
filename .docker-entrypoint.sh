#!/bin/sh
set -e

# There are two basic modes
# WORKER_SERVICE on/[off] - This will run a celery worker
# WSGI_SERVICE [on]/off - This will run gunicorn

# Options
# DB_HOST [db] - Name of the DB host
# SKIP_SQL on/[off] - Skips checking of MySQL Server
# RABBITMQ_HOST [rabbitmq] - Name of the RabbitMQ Server
# WEBPACK_STATIC on/[off] - Builds webpack
# COLLECT_STATIC on/[off] - Runs collectstatic
# MIBRATE_DB on/[off] - Migrate DB

# WORKER_SERVICE Options
# CELERY_QUEUE [celery,priority,localhost] List of worker queues
# CELERY_BEAT [-B] Run Celery Beat

# GUNICORN_SERVICE Options
# GUNICORN_WORKERS [3]  Number of workers
# To use this simply run docker run -it -p 8000:8000

# We use a Docker service run from inside the Worker container for OpenStudio-ERI runs,
# so we need the docker daemon to be running
echo >&2 "Launching docker daemon..."
# Restarting the machine can leave the docker.pid file orphaned, which will stop Docker from
# launching after reboot. Deleting the file if it is present solves this.
rm -f /var/run/docker.pid
(nohup dockerd &)

if [ "x${SKIP_SQL:-off}" != "xon" ]; then
    echo >&2 "Checking database connection..."
    until nc -w3 ${DB_HOST:-db} 3306 >/dev/null &>2; do
        echo >&2 " Waiting for database (${DB_HOST:-db}) connection..."
        sleep 1
    done
    echo >&2 "SQL is up - continuing"
else
    echo >&2 "Skipping SQL Connection"
fi

if [ "x${WEBPACK_STATIC:-off}" = 'xon' ]; then
    echo >&2 "Running webpack"
    cd /app/axis/core/static/js && npm i &&
        ./node_modules/.bin/webpack && rm -rf node_modules
fi

if [ "x${COLLECT_STATIC:-off}" = 'xon' ]; then
    echo >&2 "Collecting static (if needed) using settings ${DJANGO_SETTINGS_MODULE}"
    python manage.py collectstatic --noinput --ignore node_modules
fi

if [ "x${MIBRATE_DB:-off}" = 'xon' ]; then
    echo >&2 "Migrating data (if needed)..."
    python manage.py migrate --noinput
fi

if [ "x${CELERY_WORKER:-off}" = 'xon' ]; then
    if [ "x${SKIP_RABBITMQ:-on}" != "xon" ]; then
        echo >&2 "Checking RabbitMQ connection..."
        until nc -w3 ${RABBITMQ_HOST:-rabbitmq} 15672 >/dev/null &>2; do
            echo >&2 " Waiting for rabbitmq (${RABBITMQ_HOST:-rabbitmq}) connection..."
            sleep 1
        done
        echo >&2 "RabbitMQ is up - continuing"
    else
        echo >&2 "Skipping RabbitMQ Connection"
    fi
    cd /app
    echo >&2 "Starting $(which celery)"
    watchmedo auto-restart --patterns='*.py' --recursive -- $(which celery) -A celeryapp worker \
    --events -Q ${CELERY_QUEUE:-celery,priority,localhost} ${CELERY_BEAT:---beat}
elif [ "x${FRONTEND_ONLY:-off}" = 'xon' ]; then
    echo >&2 "Starting $(which gunicorn) with settings ${DJANGO_SETTINGS_MODULE}"
    $(which gunicorn) --bind :8000 --reload --workers ${GUNICORN_WORKERS:-3} wsgi:application
fi

exec "$@"
