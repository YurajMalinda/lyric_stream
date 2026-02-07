#!/bin/bash
# Run the typewriter song player (activates virtual environment and runs play.py)

cd "$(dirname "$0")"
source .venv/bin/activate
python3 play.py
