#!/bin/bash
echo "🚀 Starting Mammotion Web Server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not detected. Activating..."
    source venv/bin/activate
fi

# Start the server
python -m uvicorn src.mammotion_web.app:app --host 0.0.0.0 --port 8000 --reload --log-level info
