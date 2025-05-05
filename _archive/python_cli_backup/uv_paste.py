#!/usr/bin/env python3
"""
Tool for pasting text into AI chat interfaces using UV (ultraviolet) automation
"""

import os
import sys
import time
import argparse
import logging
import pyautogui
import pyperclip
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("uv_paste.log"),
        logging.StreamHandler()
    ]
)

# Directory to save screenshots if debug is enabled
DEBUG_DIR = "debug"

def save_screenshot(name, debug=False):
    """Save a screenshot for debugging purposes"""
    if not debug:
        return None
    
    # Ensure debug directory exists
    os.makedirs(DEBUG_DIR, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"{name}_{timestamp}.png"
    filepath = os.path.join(DEBUG_DIR, filename)
    
    # Take and save screenshot
    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)
    logging.info(f"Saved screenshot to {filepath}")
    return filepath

def paste_text_to_chat(text, site_config, wait_time=3, debug=False):
    """
    Paste text to chat interface using UV-based approach with direct coordinates
    
    Args:
        text: Text to paste
        site_config: Dictionary with site configuration
        wait_time: Time to wait before starting
        debug: Whether to save debug screenshots
    
    Returns:
        True if successful, False otherwise
    """
    # Validate inputs
    if not text or not isinstance(text, str):
        logging.error("No valid text provided to paste")
        return False
    
    if not site_config or not isinstance(site_config, dict):
        logging.error("No valid site configuration provided")
        return False
    
    # Extract configuration
    input_coords = site_config.get('input_coords')
    send_coords = site_config.get('send_coords')
    use_enter = site_config.get('use_enter', False)
    
    if not input_coords and not isinstance(input_coords, tuple) and len(input_coords) != 2:
        logging.error("Invalid input coordinates in site configuration")
        return False
    
    if not use_enter and (not send_coords or not isinstance(send_coords, tuple) or len(send_coords) != 2):
        logging.error("Invalid send coordinates in site configuration and use_enter not enabled")
        return False
    
    # Wait for user to position window
    print(f"\nWill paste text in {wait_time} seconds.")
    print("Please position your browser window showing the chat interface.")
    for i in range(wait_time, 0, -1):
        print(f"{i}...", end=" ", flush=True)
        time.sleep(1)
    print("Starting!")
    
    try:
        # Save initial screenshot
        save_screenshot("before_paste", debug)
        
        # Copy text to clipboard
        logging.info(f"Copying text to clipboard: {text[:50]}...")
        pyperclip.copy(text)
        time.sleep(0.5)
        
        # Click input field
        logging.info(f"Clicking input field at {input_coords}")
        pyautogui.moveTo(input_coords[0], input_coords[1], duration=0.5)
        pyautogui.click()
        time.sleep(0.3)
        
        # Select all existing text (if any)
        logging.info("Selecting all existing text")
        if sys.platform == 'darwin':  # macOS
            pyautogui.hotkey('command', 'a')
        else:  # Windows/Linux
            pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.3)
        
        # Paste text
        logging.info("Pasting text")
        if sys.platform == 'darwin':  # macOS
            pyautogui.hotkey('command', 'v')
        else:  # Windows/Linux
            pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        
        # Save screenshot after pasting
        save_screenshot("after_paste", debug)
        
        # Send the message
        if use_enter:
            logging.info("Pressing Enter to send")
            pyautogui.press('enter')
        else:
            logging.info(f"Clicking send button at {send_coords}")
            pyautogui.moveTo(send_coords[0], send_coords[1], duration=0.5)
            pyautogui.click()
            
        # Save screenshot after sending
        save_screenshot("after_send", debug)
        
        print("\nSuccess! Text was pasted and sent.")
        return True
        
    except Exception as e:
        logging.error(f"Error during text pasting: {e}")
        print(f"\nError occurred: {e}")
        return False

def load_site_config(site_name, config_file="uv_sites.json"):
    """
    Load site configuration from config file
    
    Args:
        site_name: Name of the site
        config_file: Path to config file
    
    Returns:
        Site configuration dictionary or None if not found
    """
    # Default configuration file path
    if not os.path.isabs(config_file):
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_file)
    
    # Check if config file exists
    if not os.path.exists(config_file):
        # Create default config if it doesn't exist
        default_config = {
            "perplexity": {
                "input_coords": [840, 900],
                "send_coords": [1050, 900],
                "use_enter": True
            },
            "qwen": {
                "input_coords": [840, 920],
                "send_coords": [1080, 920],
                "use_enter": True
            },
            "default": {
                "input_coords": [840, 900],
                "send_coords": [1050, 900],
                "use_enter": True
            }
        }
        
        # Create the config file
        try:
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            logging.info(f"Created default configuration file: {config_file}")
        except Exception as e:
            logging.error(f"Failed to create default configuration file: {e}")
            return None
    
    # Load configuration
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Get site config or use default
        site_config = config.get(site_name) or config.get("default")
        
        if site_config:
            # Convert string coordinates to tuples if needed
            if "input_coords" in site_config and isinstance(site_config["input_coords"], list):
                site_config["input_coords"] = tuple(site_config["input_coords"])
            if "send_coords" in site_config and isinstance(site_config["send_coords"], list):
                site_config["send_coords"] = tuple(site_config["send_coords"])
            
            return site_config
        else:
            logging.error(f"No configuration found for site: {site_name}")
            return None
            
    except Exception as e:
        logging.error(f"Error loading site configuration: {e}")
        return None

def update_site_config(site_name, input_x, input_y, send_x, send_y, use_enter=False, config_file="uv_sites.json"):
    """
    Update site configuration
    
    Args:
        site_name: Name of the site
        input_x, input_y: Coordinates of input field
        send_x, send_y: Coordinates of send button
        use_enter: Whether to use Enter key instead of clicking send button
        config_file: Path to config file
    
    Returns:
        True if successful, False otherwise
    """
    # Default configuration file path
    if not os.path.isabs(config_file):
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_file)
    
    # Load existing config or create new one
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {}
    except Exception as e:
        logging.error(f"Error loading existing configuration: {e}")
        config = {}
    
    # Update config
    config[site_name] = {
        "input_coords": [input_x, input_y],
        "send_coords": [send_x, send_y],
        "use_enter": use_enter
    }
    
    # Save config
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        logging.info(f"Updated configuration for site: {site_name}")
        return True
    except Exception as e:
        logging.error(f"Error saving configuration: {e}")
        return False

def main():
    """Main entry point for the UV paste tool"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Paste text into AI chat interfaces using UV approach")
    
    parser.add_argument("text", nargs="?", default=None, help="Text to paste (if not provided, stdin or a file is used)")
    parser.add_argument("-f", "--file", help="File containing text to paste")
    parser.add_argument("-s", "--site", default="default", help="Site identifier (default: default)")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode with screenshots")
    parser.add_argument("-w", "--wait", type=int, default=3, help="Time to wait before starting (to position window)")
    
    # Configuration parameters
    parser.add_argument("--config", help="Path to site configuration file")
    parser.add_argument("--update-config", action="store_true", help="Update site configuration")
    parser.add_argument("--input-x", type=int, help="X coordinate of input field")
    parser.add_argument("--input-y", type=int, help="Y coordinate of input field")
    parser.add_argument("--send-x", type=int, help="X coordinate of send button")
    parser.add_argument("--send-y", type=int, help="Y coordinate of send button")
    parser.add_argument("--use-enter", action="store_true", help="Use Enter key instead of clicking send button")
    
    args = parser.parse_args()
    
    # Handle configuration update
    if args.update_config:
        if not args.site or not args.input_x or not args.input_y:
            print("Error: Site name, input-x, and input-y required for configuration update")
            return 1
        
        # For send button, either coordinates or use-enter required
        if not args.use_enter and (not args.send_x or not args.send_y):
            print("Error: Either send-x and send-y or use-enter required for configuration update")
            return 1
        
        # Update configuration
        success = update_site_config(
            args.site, 
            args.input_x, 
            args.input_y, 
            args.send_x or 0, 
            args.send_y or 0, 
            args.use_enter,
            args.config
        )
        
        if success:
            print(f"Configuration for site '{args.site}' updated successfully")
        else:
            print(f"Failed to update configuration for site '{args.site}'")
        
        return 0 if success else 1
    
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
            print(f"Error: {e}")
            return 1
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
        print("Error: No text provided to paste")
        return 1
    
    # Load site configuration
    site_config = load_site_config(args.site, args.config)
    if not site_config:
        print(f"Error: No configuration found for site '{args.site}'")
        return 1
    
    # Paste text to chat
    success = paste_text_to_chat(
        text_to_paste,
        site_config,
        args.wait,
        args.debug
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())