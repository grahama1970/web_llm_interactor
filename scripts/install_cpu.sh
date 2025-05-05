#!/bin/bash

# Install base dependencies
pip install -e .

# Install CPU version of PyTorch
pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cpu