#!/bin/bash

# Made by: Henrik Lagrosen

# This script is used for running the application within the docker container

# Setup job
python manage.py setup_models

if [ "$RUN_MODE" = "dev" ]; then
    python manage.py runserver 0.0.0.0:8000
elif [ "$RUN_MODE" = "prod" ]; then
    python manage.py collectstatic --noinput
    gunicorn fraud_detection.wsgi:application --bind 0.0.0.0:8000 --workers 3
else
    echo "Invalid argument: $RUN_MODE"
    exit 1
fi
