#!/bin/bash
# Real Estate Investment Simulator - Startup Script

echo "🏠 Real Estate Investment Simulator"
echo "===================================="
echo ""

# Activate virtual environment
echo "📦 Activating virtual environment..."
source /home/chinmay/projects/tradeselect/trader-ai/trader/bin/activate

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null
then
    echo "❌ Streamlit not found. Installing required packages..."
    pip install -r requirements.txt
fi

# Start the application
echo "🚀 Starting Streamlit application..."
echo ""
echo "The app will open in your browser at http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app.py
