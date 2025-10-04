#!/bin/bash

# EcoPredict Startup Script
echo "🚀 Starting EcoPredict..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js v16 or higher."
    exit 1
fi

# Start backend
echo "🔧 Starting backend server..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if requirements.txt is newer than last install
if [ requirements.txt -nt venv/pyvenv.cfg ]; then
    echo "📥 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Start Flask server in background
echo "🌐 Starting Flask API server on http://localhost:5000"
python main.py &
BACKEND_PID=$!

# Go back to root directory
cd ..

# Start frontend
echo "🎨 Starting frontend server..."
cd frontend

# Install dependencies if package.json is newer than node_modules
if [ package.json -nt node_modules/.package-lock.json ]; then
    echo "📥 Installing Node.js dependencies..."
    npm install
fi

# Start React development server
echo "🌐 Starting React development server on http://localhost:3000"
npm start &
FRONTEND_PID=$!

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT

echo "✅ EcoPredict is running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:5000"
echo "   Press Ctrl+C to stop both servers"

# Wait for both processes
wait