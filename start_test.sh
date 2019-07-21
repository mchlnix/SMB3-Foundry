#!/usr/bin/env bash

# start the editor in the background, saving its process ID

python3 smb3-foundry.py &

FOUNDRY_PID=$!

# wait a 10 seconds

sleep 10

# if it is still open, we assume it started correctly

if ps aux  | grep -v "grep" | grep "smb3-foundry.py" >/dev/null; then
    kill "$FOUNDRY_PID"

    exit 0
else
    exit 1
fi