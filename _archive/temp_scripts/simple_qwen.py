#!/usr/bin/env python3
"""
Simplified Qwen CLI without vision dependencies.
"""

import os
import sys
import time
import json
import logging
import argparse
import random
import pyautogui
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("qwen_chat.log"), logging.StreamHandler()],
)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Simple Qwen CLI")
    parser.add_argument(
        "--query", 
        type=str, 
        help="Query to send to the AI"
    )
    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_args()
    
    if not args.query:
        print("Error: No query provided. Use --query \"Your query here\"")
        return 1
    
    print("\n" + "=" * 60)
    print("Simple Qwen CLI - No Vision Dependencies")
    print(f"Query: {args.query}")
    print("=" * 60 + "\n")
    
    # Try to take a screenshot to verify PyAutoGUI is working
    try:
        print("Testing screenshot capability...")
        screenshot = pyautogui.screenshot()
        screenshot_path = os.path.join("screenshots", f"test_{int(time.time())}.png")
        os.makedirs("screenshots", exist_ok=True)
        screenshot.save(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return 1
    
    print("\nBasic functionality test complete!")
    print(f"Your query was: {args.query}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())