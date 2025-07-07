#!/bin/bash
# Neon Pacman Game Launcher

echo "🎮 Starting Neon Pacman with AI..."
echo "=================================="

# Check if virtual environment exists
if [ -d "pacman_env" ]; then
    echo "📦 Activating virtual environment..."
    source pacman_env/bin/activate
fi

# Check if dependencies are installed
python3 -c "import pygame, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependencies not found. Installing..."
    pip install -r requirements.txt
fi

# Run the game
echo "🚀 Launching game..."
python3 pacman_neon.py
