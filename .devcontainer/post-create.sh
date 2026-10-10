#!/bin/bash

echo "=== Installing System Tools ==="
pipx install uv

echo "=== Syncing Dependencies ==="
uv sync
echo "=== Environment Ready! ==="

echo "Python Version:"
python --version

echo "UV Version"
uv --version