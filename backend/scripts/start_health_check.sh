#!/bin/bash

# Start the health check service
echo "🏥 Starting AI Block Bookkeeper Health Check Service..."

# Get the directory where this script is located and go up one level to backend
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
cd "$BACKEND_DIR"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found at venv/bin/activate"
    echo "   Make sure you're running this from the backend directory"
    exit 1
fi

# Check if health_check.py exists
if [ -f "health_check.py" ]; then
    echo "✅ Found health_check.py"
    python health_check.py
else
    echo "❌ health_check.py not found in current directory"
    echo "   Current directory: $(pwd)"
    echo "   Available files:"
    ls -la
    exit 1
fi
