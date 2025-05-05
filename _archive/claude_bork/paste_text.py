#!/usr/bin/env python3
"""
Tool for pasting text into AI chat interfaces using vision-based element detection
"""

import os
import sys
import time
import argparse
import logging
import random
from pathlib import Path

# Import local modules
from .human_input import HumanInput
from .vision_detection import VisionDetector
from .text_paste_utils import TextPaster

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("paste_text.log"),
        logging.StreamHandler()
    ]
)

def main():
    """Main entry point for the text pasting tool"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Paste text into AI chat interfaces using vision detection")
    
    parser.add_argument("text", nargs="?", default=None, help="Text to paste (if not provided, stdin or a file is used)")
    parser.add_argument("-f", "--file", help="File containing text to paste")
    parser.add_argument("-s", "--site", choices=["auto", "qwen", "perplexity"], default="auto", 
                        help="Target site identifier (default: auto)")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode with screenshots")
    parser.add_argument("-w", "--wait", type=int, default=3, 
                        help="Time to wait before starting (to position window)")
    parser.add_argument("--no-keyboard", action="store_true", 
                        help="Don't use keyboard shortcuts for pasting")
    
    args = parser.parse_args()
    
    # Get the text to paste from the appropriate source
    if args.text:
        # Use text directly from command line
        text_to_paste = args.text
    elif args.file:
        # Read text from a file
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text_to_paste = f.read()
        except Exception as e:
            logging.error(f"Failed to read text from file: {e}")
            sys.exit(1)
    elif not sys.stdin.isatty():
        # Read from stdin if it's not a terminal (e.g., piped input)
        text_to_paste = sys.stdin.read()
    else:
        # If no text is provided, prompt the user
        print("Enter the text to paste (press Ctrl+D or Ctrl+Z on a new line to finish):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            text_to_paste = "\n".join(lines)
    
    # Ensure we have text to paste
    if not text_to_paste or text_to_paste.strip() == "":
        logging.error("No text provided to paste")
        sys.exit(1)
    
    # Tell the user we're about to start
    print(f"\nWill paste text to {args.site} in {args.wait} seconds.")
    print("Please position your browser window showing the chat interface.")
    for i in range(args.wait, 0, -1):
        print(f"{i}...", end=" ", flush=True)
        time.sleep(1)
    print("Starting!")
    
    # Create required components
    human = HumanInput()
    
    # Create and initialize the vision detector
    try:
        vision = VisionDetector()
        vision.load_model()
    except Exception as e:
        logging.error(f"Failed to initialize vision detector: {e}")
        print("Error: Could not initialize the vision detector.")
        print("Make sure all required dependencies are installed.")
        sys.exit(1)
    
    # Create the text paster
    paster = TextPaster(human, vision, debug=args.debug)
    
    # Paste the text
    try:
        success = paster.paste_text_to_chat(
            text_to_paste, 
            site_id=args.site,
            use_keyboard_shortcut=not args.no_keyboard
        )
        
        if success:
            print("\nSuccess! Text was pasted and sent.")
        else:
            print("\nFailed to paste and send the text. Check the logs for details.")
    except Exception as e:
        logging.error(f"Error during text pasting: {e}")
        print(f"\nError occurred: {e}")
    finally:
        # Clean up
        try:
            vision.unload_model()
        except:
            pass
    
    # Random idle behavior to avoid detection
    if random.random() < 0.3:
        human.random_idle(random.uniform(1.0, 3.0))

if __name__ == "__main__":
    main()