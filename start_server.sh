#!/bin/bash

# Default port
PORT=8003

# Check if a port number is provided as an argument
if [ $# -eq 1 ]; then
  PORT=$1
fi

# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port $PORT