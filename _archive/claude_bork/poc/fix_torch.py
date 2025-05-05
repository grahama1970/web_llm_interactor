#!/usr/bin/env python3
"""
Fix PyTorch installation for Intel Macs.

This script detects your system configuration and installs the appropriate 
PyTorch version for your system, including special handling for Intel Macs.
"""

import os
import sys
import platform
import subprocess
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Fix PyTorch installation for your system")
    parser.add_argument("--force", action="store_true", help="Force reinstallation even if PyTorch is already installed")
    parser.add_argument("--no-confirm", action="store_true", help="Skip confirmation prompts")
    return parser.parse_args()

def run_command(cmd):
    """Run a shell command and return its output."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, text=True, 
                               capture_output=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Error: {e.stderr}"

def check_pip():
    """Check if pip is available."""
    return run_command(f"{sys.executable} -m pip --version")

def is_torch_installed():
    """Check if PyTorch is already installed."""
    try:
        import torch
        return True, torch.__version__
    except ImportError:
        return False, None

def get_system_info():
    """Get system information."""
    system = platform.system()
    machine = platform.machine()
    python_version = platform.python_version()
    
    is_intel_mac = system == "Darwin" and machine == "x86_64"
    is_apple_silicon = system == "Darwin" and machine == "arm64"
    is_windows = system == "Windows"
    is_linux = system == "Linux"
    
    return {
        "system": system,
        "machine": machine,
        "python_version": python_version,
        "is_intel_mac": is_intel_mac,
        "is_apple_silicon": is_apple_silicon,
        "is_windows": is_windows,
        "is_linux": is_linux
    }

def get_torch_install_command(system_info):
    """Get the appropriate PyTorch installation command for the system."""
    if system_info["is_intel_mac"]:
        # For Intel Macs, we need a specific version
        return "pip install torch==1.13.1 torchvision==0.14.1 -f https://download.pytorch.org/whl/torch_stable.html"
    elif system_info["is_apple_silicon"]:
        # For Apple Silicon
        return "pip install torch torchvision"
    elif system_info["is_windows"]:
        return "pip install torch torchvision"
    elif system_info["is_linux"]:
        return "pip install torch torchvision"
    else:
        return "pip install torch torchvision"  # Default fallback

def install_pytorch(system_info, force=False):
    """Install PyTorch appropriate for the system."""
    is_installed, version = is_torch_installed()
    
    if is_installed and not force:
        print(f"PyTorch {version} is already installed. Use --force to reinstall.")
        return True
    
    install_cmd = get_torch_install_command(system_info)
    success, output = run_command(install_cmd)
    
    if success:
        print("PyTorch installation completed successfully.")
        return True
    else:
        print("PyTorch installation failed.")
        print(output)
        return False

def install_dependencies():
    """Install other required dependencies."""
    dependencies = [
        "transformers",
        "pyautogui",
        "pyperclip",
        "pillow",
        "tqdm"
    ]
    
    print("Installing required dependencies...")
    deps_cmd = f"{sys.executable} -m pip install {' '.join(dependencies)}"
    success, output = run_command(deps_cmd)
    
    if success:
        print("Dependencies installed successfully.")
        return True
    else:
        print("Dependency installation failed.")
        print(output)
        return False

def main():
    args = parse_args()
    
    print("=" * 60)
    print("PyTorch Installation Helper for Vision POC Scripts")
    print("=" * 60)
    
    system_info = get_system_info()
    print(f"System: {system_info['system']} {system_info['machine']}")
    print(f"Python: {system_info['python_version']}")
    
    if system_info["is_intel_mac"]:
        print("\nDetected Intel Mac!")
        print("We'll install PyTorch 1.13.1 which is compatible with your system")
        print("Note: This version doesn't support MPS acceleration")
    
    success, _ = check_pip()
    if not success:
        print("Error: pip is not available. Please install pip first.")
        return 1
    
    if not args.no_confirm:
        confirm = input("\nReady to install PyTorch and required packages. Continue? [y/N]: ")
        if confirm.lower() != 'y':
            print("Installation cancelled.")
            return 0
    
    install_pytorch(system_info, args.force)
    install_dependencies()
    
    print("\nInstallation complete. Try running the POC scripts now.")
    print("Example: python paste_to_chat.py \"Hello world\"")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())