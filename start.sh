#!/bin/bash
echo "Starting AI News Dashboard..."
echo ""

cd "$(dirname "$0")"

source venv/bin/activate

echo "Access: http://localhost:5000"
echo "Press Ctrl+C to stop."
echo ""

python3 app.py
