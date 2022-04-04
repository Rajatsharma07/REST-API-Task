#!/usr/bin/env bash
if ! docker info > /dev/null 2>&1; then
  echo "This script uses docker, and it isn't running - please start docker and try again!"
  exit 1
fi
export FLASK_APP=app.py
export FLASK_ENV=development

export USERNAME="rajatsharma07"
export PASSWORD=$1
export IMAGE_NAME="rajatsharma07/data_scientists_builds"
export NO_CACHE="True"
export IMAGE_TAG="V1.1"

python -m flask run