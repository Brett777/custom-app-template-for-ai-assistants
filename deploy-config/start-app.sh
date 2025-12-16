#!/usr/bin/env sh

echo "=== Starting DataRobot Custom Application ==="
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"

# Get PORT from environment (DataRobot provides this)
PORT=${PORT:-8080}
echo "Starting server on port: $PORT"

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI application with uvicorn
# CRITICAL: Must bind to 0.0.0.0 (not localhost) for DataRobot
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
