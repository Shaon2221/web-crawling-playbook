#!/bin/bash

# Books Crawler - Quick Start Script

set -e

echo "=================================="
echo "Books Crawler - Quick Start"
echo "=================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command_exists python3; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION found"

if ! command_exists docker; then
    echo "Warning: Docker is not installed (optional but recommended)"
else
    echo "✓ Docker found"
fi

# Setup environment
echo ""
echo "Setting up environment..."

if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✓ .env file created (please update with your settings)"
else
    echo "✓ .env file already exists"
fi

# Create virtual environment
if [ ! -d venv ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p logs data/checkpoints data/sample
echo "✓ Directories created"

# Start MongoDB
echo ""
echo "Starting MongoDB..."
if command_exists docker; then
    if docker ps -a | grep -q mongodb; then
        echo "MongoDB container already exists"
        docker start mongodb || true
    else
        docker run -d -p 27017:27017 --name mongodb mongo:7.0
    fi
    echo "✓ MongoDB started"
else
    echo "⚠ Docker not available. Please start MongoDB manually"
fi

# Wait for MongoDB
echo ""
echo "Waiting for MongoDB to be ready..."
sleep 3

# Display next steps
echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Update .env file with your settings:"
echo "   nano .env"
echo ""
echo "2. Run the crawler:"
echo "   python -m src crawl"
echo ""
echo "3. Start the API server:"
echo "   python -m src api"
echo ""
echo "4. View API documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "For more information, see README.md"
echo ""
