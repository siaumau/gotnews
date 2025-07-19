#!/bin/bash

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo
echo "Setup complete!"
echo
echo "Please set NewsAPI key:"
echo "export NEWS_API_KEY=your_api_key_here"
echo
echo "Then run:"
echo "python app.py"
