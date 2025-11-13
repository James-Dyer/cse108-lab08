#!/bin/bash
echo "Starting Flask Backend..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "Starting Flask server on http://localhost:5000"
python app.py
