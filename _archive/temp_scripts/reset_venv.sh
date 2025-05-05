#!/bin/bash

# Clean up any existing virtual environment
echo "Cleaning up existing virtual environment..."
rm -rf .venv

# Create a fresh virtual environment  
echo "Creating new virtual environment..."
python -m venv .venv
source .venv/bin/activate

# Install basic dependencies
echo "Installing base package..."
uv pip install -e .

# Install system PyTorch directly from PyPI
echo "Installing PyTorch (system version)..."
pip install torch==2.0.1 torchvision==0.15.2

echo "Installation complete! Activate with: source .venv/bin/activate"