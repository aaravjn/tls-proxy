#!/bin/bash

# Function to handle the Ctrl+C (SIGINT) signal
trap "echo 'Stopping the script...'; kill $PID; exit 0" SIGINT

# Run the main.py file in the background
python3 main.py &
PID=$!  # Get the process ID of the Python script

# Wait for the Python script process to finish
wait $PID
