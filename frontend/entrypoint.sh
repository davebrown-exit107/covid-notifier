#!/usr/bin/env bash

poetry run flask db upgrade
poetry run gunicorn --bind=0.0.0.0:5000 covid_notifier.app:notifier_app
