#!/bin/bash

echo "=================================="
echo "   Manualarr Installation Script  "
echo "=================================="

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose is not installed."
    exit 1
fi

echo "Building and starting Manualarr..."
echo "This may take a few minutes..."

# Use "docker compose" or "docker-compose"
if docker compose version &> /dev/null; then
    docker compose down --remove-orphans 2>/dev/null
    docker compose up -d --build
else
    docker-compose down --remove-orphans 2>/dev/null
    docker-compose up -d --build
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Success! Manualarr is running."
    echo "Access the application at: http://localhost:8081"
    echo "To stop: docker-compose down"
else
    echo "❌ Error: Failed to start containers."
fi
