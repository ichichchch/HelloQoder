#!/bin/bash
echo "========================================"
echo "  GLIMMER UI - Frontend"
echo "========================================"
echo

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    echo
fi

echo "Starting development server..."
npm run dev
