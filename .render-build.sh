#!/usr/bin/env bash
# .render-build.sh
set -o errexit

echo "Installing Python dependencies..."
pip install --no-cache-dir -r backend/requirements.txt

# Add any additional build steps here if needed