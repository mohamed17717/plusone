#!/bin/bash -x

python manage.py migrate --noinput && python manage.py collectstatic --noinput || exit 1
exec "$@"