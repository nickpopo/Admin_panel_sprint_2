#!/bin/bash

# wait for Postgres to start
function postgres_ready(){
python << END
import sys
import os
import psycopg2
dsn = {
        'dbname': os.environ.get('DJANGO_POSTGRES_DBNAME'),
        'user': os.environ.get('DJANGO_POSTGRES_USER'),
        'password': os.environ.get('DJANGO_POSTGRES_PASSWORD'),
        'host': os.environ.get('DJANGO_POSTGRES_HOST', '127.0.0.1'),
        'port': os.environ.get('DJANGO_POSTGRES_PORT', '5432'),
}
try:
    conn = psycopg2.connect(**dsn)
except psycopg2.OperationalError:
    sys.exit(-1)
conn.close()
sys.exit(0)
END
}

until postgres_ready; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

python manage.py migrate

gunicorn -c gunicorn_conf.py config.wsgi --reload