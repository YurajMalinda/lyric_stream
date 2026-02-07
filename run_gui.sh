#!/bin/bash
# Run the GUI version of the typewriter song player

cd "$(dirname "$0")"
source .venv/bin/activate
python3 gui.py
