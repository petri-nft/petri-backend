#!/bin/bash

# Plant a Tree NFT - Full Stack Startup Script
# Starts both Backend (FastAPI) and Frontend (Vite) servers

set -e

PROJECT_ROOT="/home/admin/Desktop/Petri"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "🌳 Plant a Tree NFT - Full Stack Startup"
echo "=========================================="
echo ""

# Check if both directories exist
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Backend directory not found: $BACKEND_DIR"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Frontend directory not found: $FRONTEND_DIR"
    exit 1
fi

# Start Backend
echo "🚀 Starting Backend Server (FastAPI)..."
cd "$BACKEND_DIR"
if [ -d "venv" ]; then
    source venv/bin/activate
fi
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
echo "   📍 API URL: http://localhost:8000"
echo "   📍 Docs: http://localhost:8000/docs"
echo ""

# Wait a moment for backend to start
sleep 2

# Start Frontend
echo "🚀 Starting Frontend Server (Vite)..."
cd "$FRONTEND_DIR"

# Check if node_modules exists, if not install dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    if command -v bun &> /dev/null; then
        bun install
    elif command -v npm &> /dev/null; then
        npm install
    else
        echo "❌ Neither bun nor npm found. Please install Node.js/npm or Bun."
        kill $BACKEND_PID
        exit 1
    fi
fi

# Start frontend dev server
if command -v bun &> /dev/null; then
    bun run dev &
else
    npm run dev &
fi
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo "   📍 Frontend URL: http://localhost:5173"
echo ""

echo "=========================================="
echo "✨ Full Stack Running!"
echo "=========================================="
echo ""
echo "🌐 Frontend:  http://localhost:5173"
echo "🔌 Backend:   http://localhost:8000"
echo "📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Keep script running
wait
