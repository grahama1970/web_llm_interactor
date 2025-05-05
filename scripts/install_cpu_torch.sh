#!/bin/bash

# Install base package without PyTorch
uv pip install -e ".[vision]"

# Install latest CPU-only PyTorch with the right version
uv pip install "torch>=2.0.0,<2.1.0" "torchvision>=0.15.0,<0.16.0" accelerate --index-url https://download.pytorch.org/whl/cpu