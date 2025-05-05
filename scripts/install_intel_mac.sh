#!/bin/bash
# This script installs the PyTorch nightly build with the MPS support for Intel Macs

# Check if we're on an Intel Mac
system=$(uname -s)
cpu=$(uname -m)

if [ "$system" != "Darwin" ] || [ "$cpu" != "x86_64" ]; then
    echo "This script is specifically for Intel Macs. Your system is: $system $cpu"
    echo "You don't need this special installation."
    exit 1
fi

echo "======================================================================"
echo "Installing PyTorch with MPS support for Intel Mac"
echo "======================================================================"
echo ""
echo "This will install the pre-release nightly build of PyTorch that"
echo "includes a community fix to enable MPS acceleration on Intel Macs."
echo ""
echo "For more information, see: https://github.com/pytorch/pytorch/pull/77764"
echo ""

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "WARNING: It appears you're not in a virtual environment."
    echo "It's recommended to use a virtual environment for this installation."
    echo ""
    read -p "Continue with installation anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation canceled."
        exit 1
    fi
fi

echo "Installing PyTorch from nightly builds..."
pip install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cpu

# Set the environment variable globally if possible
echo ""
echo "Setting PYTORCH_ENABLE_MPS_FALLBACK=1 in shell profile..."

# Determine which shell is being used and update the appropriate profile file
SHELL_NAME=$(basename "$SHELL")
if [ "$SHELL_NAME" = "bash" ]; then
    PROFILE_FILE="$HOME/.bash_profile"
    if [ ! -f "$PROFILE_FILE" ]; then
        PROFILE_FILE="$HOME/.bashrc"
    fi
elif [ "$SHELL_NAME" = "zsh" ]; then
    PROFILE_FILE="$HOME/.zshrc"
else
    echo "Unsupported shell: $SHELL_NAME"
    echo "Please manually add 'export PYTORCH_ENABLE_MPS_FALLBACK=1' to your shell profile."
    PROFILE_FILE=""
fi

if [ -n "$PROFILE_FILE" ]; then
    if grep -q "PYTORCH_ENABLE_MPS_FALLBACK" "$PROFILE_FILE"; then
        echo "Environment variable already exists in $PROFILE_FILE"
    else
        echo "Adding environment variable to $PROFILE_FILE"
        echo "" >> "$PROFILE_FILE"
        echo "# Enable MPS support for PyTorch on Intel Macs" >> "$PROFILE_FILE"
        echo "export PYTORCH_ENABLE_MPS_FALLBACK=1" >> "$PROFILE_FILE"
    fi
fi

# Set the variable for the current session too
export PYTORCH_ENABLE_MPS_FALLBACK=1

echo ""
echo "Installing other required packages..."
pip install transformers accelerate pillow pyautogui

echo ""
echo "======================================================================"
echo "Installation complete"
echo "======================================================================"
echo ""
echo "PyTorch with MPS support for Intel Mac has been installed."
echo "The PYTORCH_ENABLE_MPS_FALLBACK=1 environment variable has been set."
echo ""
echo "For this session, we've already set the environment variable."
echo "For future sessions, you may need to restart your terminal or run:"
echo "  export PYTORCH_ENABLE_MPS_FALLBACK=1"
echo ""
echo "To test if MPS is working, run:"
echo ""
echo "python3 -c \"import torch; print('MPS available:', torch.backends.mps.is_available())\""
echo ""
echo "It should output 'MPS available: True'"
echo ""