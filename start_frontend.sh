#!/bin/bash
echo "Starting React Frontend..."
cd client
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi
echo "Starting Vite dev server..."
npm run dev
