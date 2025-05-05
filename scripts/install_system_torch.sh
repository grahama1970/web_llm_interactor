#!/bin/bash

# Install base package without PyTorch
uv pip install -e ".[vision]"

# Install system PyTorch (from PyPI, not pytorch.org)
uv pip install torch torchvision accelerate