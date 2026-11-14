#!/usr/bin/env bash
# Render build script. Exit immediately if any command fails.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input

# Free plan has no Shell tab, so seed demo data from the build when asked.
# Set RUN_SEED=true for one deploy, then remove it.
if [ "$RUN_SEED" = "true" ]; then
  python seed_data.py
fi
