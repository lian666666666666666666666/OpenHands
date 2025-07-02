#!/bin/bash

# Run the Luxury Maze Adventure locally without Docker

# Navigate to the project directory
cd "$(dirname "$0")"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Install dependencies if not already installed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment and installing dependencies..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run the web interface
echo "Starting Luxury Maze Adventure web interface..."
python3 run.py --mode web --port 12000

# Deactivate virtual environment when done
deactivate
