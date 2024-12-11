#!/bin/bash

# This script is used for running the application within the docker container

python manage.py setup_models

if [ "$RUN_MODE" = "dev" ]; then
    python manage.py runserver 0.0.0.0:8000
elif [ "$RUN_MODE" = "prod" ]; then
    gunicorn --bind 0.0.0.0:8000
else
    echo "Invalid argument: $RUN_MODE"
    exit 1
fi
