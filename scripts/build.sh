#!/bin/bash
# Exit on error
set -e

# Change directory to project root (one level up from scripts/)
cd "$(dirname "$0")/.."

echo "Installing PyInstaller..."
pip3 install pyinstaller

echo "Building WAConnectPro..."
# Note: Use ':' as separator for --add-data on Linux/Mac
python3 -m PyInstaller --name WAConnectPro --onefile --add-data "templates:templates" app.py

echo "Build complete. Executable is in the 'dist' folder."
