#!/bin/bash
# Docker startup helper script

set -e

echo "🚀 RAG Service - Docker Startup"
echo "================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "📋 Please copy .env.example to .env and configure your settings."
    exit 1
fi

echo "✅ .env file found"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p documents
mkdir -p logs

echo "✅ Directories created"

# Check Docker installation
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    exit 1
fi

echo "✅ Docker is installed"

# Check Docker Compose installation
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed!"
    exit 1
fi

echo "✅ Docker Compose is installed"

# Build images
echo ""
echo "🔨 Building Docker images..."
docker-compose build --no-cache

echo ""
echo "✅ Docker images built successfully"

# Display next steps
echo ""
echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "To start the services, run:"
echo "  docker-compose up -d"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop the services:"
echo "  docker-compose down"
echo ""
echo "API will be available at: http://localhost:8000"
echo "Frontend will be available at: http://localhost:8501"
echo ""
