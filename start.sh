#!/bin/bash
# DILBAR < 3 — bot startup script
# Run this on your AWS EC2 instance to start the bot

cd "$(dirname "$0")"

while true; do
    echo "[$(date)] Starting DILBAR < 3 bot..."
    python3 main.py
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ]; then
        echo "[$(date)] Bot exited cleanly. Restarting in 5 seconds..."
    else
        echo "[$(date)] Bot crashed (exit code $EXIT_CODE). Restarting in 5 seconds..."
    fi
    sleep 5
done
