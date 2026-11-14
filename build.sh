#!/usr/bin/env bash
# Render build script for AniNova. Exit immediately if any command fails.
set -o errexit

echo "📦 Installing Python Dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🎨 Collecting Static Files for WhiteNoise..."
python manage.py collectstatic --no-input

echo "🗄️ Applying Database Migrations..."
python manage.py migrate --no-input

echo "⚡ Seeding AniNova Anime Catalog & Superuser..."
if [ "$SKIP_SEED" != "true" ]; then
  python seed_data.py || true
fi

echo "✅ AniNova Build Completed Successfully!"
