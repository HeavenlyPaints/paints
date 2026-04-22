#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Safely creating missing database tables..."
python -c "from run import app; from app import db; app.app_context().push(); db.create_all()"

echo "Build script completed successfully!"
