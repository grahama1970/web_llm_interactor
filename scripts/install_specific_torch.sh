#!/bin/bash

# Install base package 
uv pip install -e ".[vision]"

# Install specific PyTorch 2.0.1 CPU only
uv pip install torch==2.0.1 torchvision==0.15.2 accelerate==0.22.0 --index-url https://download.pytorch.org/whl/cpu