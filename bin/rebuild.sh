#!/bin/bash

# Run from the repo root regardless of where the script was invoked from.
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

echo "Rebuilding and reinstalling speaking-clock..."

# Uninstall previous version if it exists
echo "Uninstalling previous version..."
pipx uninstall speaking-clock 2>/dev/null || echo "No previous installation found."

# Clean up build artifacts
echo "Cleaning up build artifacts..."
rm -rf build/ dist/ speaking_clock.egg-info/ || echo "No build artifacts to clean."

# Build package
echo "Building package..."
pip install --upgrade build
python -m build

# Install with pipx
echo "Installing with pipx..."
pipx install dist/*.whl

echo "Installation complete. You can now run 'speak-time' command from any directory."
