#!/usr/bin/env python
"""
Simple test script to verify imports are working correctly.
"""

import sys

def main():
    """Test importing key modules to verify installation."""
    print(f"Python version: {sys.version}")
    
    try:
        import pyautogui
        print(f"PyAutoGUI version: {pyautogui.__version__}")
    except ImportError:
        print("Failed to import pyautogui")
    
    try:
        import pyperclip
        print(f"Pyperclip version: {pyperclip.__version__}")
    except ImportError:
        print("Failed to import pyperclip")
    
    try:
        from PIL import Image, __version__
        print(f"PIL/Pillow version: {__version__}")
    except ImportError:
        print("Failed to import PIL")
    
    try:
        import pytesseract
        print(f"Pytesseract version: {pytesseract.__version__}")
    except ImportError:
        print("Failed to import pytesseract")
    
    try:
        import requests
        print(f"Requests version: {requests.__version__}")
    except ImportError:
        print("Failed to import requests")
    
    try:
        import loguru
        print(f"Loguru version: {loguru.__version__}")
    except ImportError:
        print("Failed to import loguru")
    
    try:
        import dotenv
        print(f"python-dotenv version: {dotenv.__version__}")
    except ImportError:
        print("Failed to import dotenv")
    
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
    except ImportError:
        print("Failed to import torch")
    
    try:
        import torchvision
        print(f"TorchVision version: {torchvision.__version__}")
    except ImportError:
        print("Failed to import torchvision")
    
    try:
        import transformers
        print(f"Transformers version: {transformers.__version__}")
    except ImportError:
        print("Failed to import transformers")
    
    try:
        import accelerate
        print(f"Accelerate version: {accelerate.__version__}")
    except ImportError:
        print("Failed to import accelerate")
    
    # Try importing our own modules
    try:
        from src import browser, human_input, utils
        print("Successfully imported src modules")
    except ImportError as e:
        print(f"Failed to import src modules: {e}")

if __name__ == "__main__":
    main()