#!/bin/bash

# Build and run the Docker container for the Luxury Maze Adventure

# Start Docker daemon if not running
if ! docker info > /dev/null 2>&1; then
    echo "Starting Docker daemon..."
    sudo dockerd > /tmp/docker.log 2>&1 &
    sleep 5
fi

# Navigate to the project directory
cd "$(dirname "$0")"

# Build and run with Docker Compose
echo "Building and starting the Luxury Maze Adventure..."
docker-compose up --build -d

echo "Maze game is running at http://localhost:12000"
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
