#!/bin/bash

# Quick Start Script for Plant a Tree Backend
# This script sets up the backend environment and starts the server

set -e

echo "========================================="
echo "Plant a Tree - Backend Quick Start"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠ .env created - Please update DATABASE_URL with your PostgreSQL credentials"
    echo ""
    read -p "Have you configured the DATABASE_URL in .env? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please edit .env and run the script again"
        exit 1
    fi
fi

# Initialize database
echo ""
echo "Initializing database..."
python -m app.database.init
echo "✓ Database initialized"

# Start the server
echo ""
echo "========================================="
echo "Starting FastAPI server..."
echo "========================================="
echo ""
echo "Server URL: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
