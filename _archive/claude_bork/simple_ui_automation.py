#!/usr/bin/env python3
"""
Simple UI Automation Tool for Chat Interfaces

This script provides basic UI automation for chat interfaces using PyAutoGUI and 
traditional image recognition techniques. It doesn't require PyTorch or ML models,
making it compatible with all platforms including Intel Macs.

Features:
- Screenshot-based element detection
- Mock functionality to simulate vision model behavior
- OS-level keyboard and mouse simulation

Usage:
  python simple_ui_automation.py --query "Your query text"
"""

import os
import sys
import time
import argparse
import random
import logging
import json
from pathlib import Path
import pyautogui
import pyperclip
from PIL import Image, ImageDraw

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("ui_automation.log"), logging.StreamHandler()]
)

# Configure PyAutoGUI
pyautogui.FAILSAFE = True  # Move mouse to top-left to abort
pyautogui.PAUSE = 0.5  # Small pause between actions

# Create debug directory
DEBUG_DIR = "debug"
os.makedirs(DEBUG_DIR, exist_ok=True)

class SimpleUIAutomation:
    """Simple UI automation class for chat interfaces."""
    
    def __init__(self, site_name="generic", debug=False):
        """Initialize the UI automation with optional debuggable vision."""
        self.site_name = site_name
        self.debug = debug
        self.screenshot_dir = DEBUG_DIR
        
        logging.info(f"Initialized UI automation for {site_name}")
        print(f"Simple UI Automation initialized for {site_name}")

    def capture_screenshot(self, prefix="screenshot"):
        """Capture a screenshot of the entire screen."""
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        screenshot = pyautogui.screenshot()
        image = screenshot.copy()
        
        if self.debug:
            filepath = os.path.join(self.screenshot_dir, f"{prefix}_{timestamp}.png")
            image.save(filepath)
            logging.info(f"Saved screenshot to {filepath}")
            
        return image, timestamp

    def detect_chat_input(self):
        """
        Detect the chat input area using simple heuristics.
        
        This is a simplified version that makes educated guesses based on common
        UI patterns in chat interfaces. For a real application, this would need
        to be enhanced with more sophisticated detection.
        """
        # Take a screenshot
        screenshot, _ = self.capture_screenshot("detect")
        
        # Get screen dimensions
        screen_width, screen_height = screenshot.size
        
        # Common chat input positions (based on typical UI patterns)
        if self.site_name == "perplexity":
            # For Perplexity, the input is typically at the bottom center
            # This is an approximation based on common UI patterns
            x1 = int(screen_width * 0.25)
            y1 = int(screen_height * 0.85)
            x2 = int(screen_width * 0.75)
            y2 = int(screen_height * 0.95)
        elif self.site_name == "qwen":
            # For Qwen, similar position but might vary
            x1 = int(screen_width * 0.2)
            y1 = int(screen_height * 0.8)
            x2 = int(screen_width * 0.8)
            y2 = int(screen_height * 0.9)
        else:
            # Generic fallback that works for most chat interfaces
            # Most chat inputs are at the bottom of the screen, center-aligned
            x1 = int(screen_width * 0.2)
            y1 = int(screen_height * 0.8)
            x2 = int(screen_width * 0.8)
            y2 = int(screen_height * 0.95)
        
        # Visualize the detected area if debug is enabled
        if self.debug:
            self._visualize_area(screenshot, x1, y1, x2, y2, "detected_input")
            
        # Format the result similar to ML-based detection
        width = x2 - x1
        height = y2 - y1
        center_x = x1 + width // 2
        center_y = y1 + height // 2
        
        logging.info(f"Estimated chat input: {width}x{height} at ({x1},{y1}) to ({x2},{y2})")
        
        return {
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "width": width,
            "height": height,
            "center_x": center_x,
            "center_y": center_y
        }
    
    def _visualize_area(self, image, x1, y1, x2, y2, prefix="area"):
        """Draw a box on the image to visualize the detected area."""
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        draw_image = image.copy()
        draw = ImageDraw.Draw(draw_image)
        draw.rectangle([(x1, y1), (x2, y2)], outline="red", width=3)
        
        filepath = os.path.join(self.screenshot_dir, f"{prefix}_{timestamp}.png")
        draw_image.save(filepath)
        logging.info(f"Saved visualization to {filepath}")
    
    def add_human_randomness(self, x, y, duration=None):
        """Add slight randomness to coordinates and movement for human-like interaction."""
        # Add minor pixel offset (±5 pixels) for natural variation
        rand_x = x + random.uniform(-5, 5)
        rand_y = y + random.uniform(-5, 5)
        
        # Randomize duration slightly if provided
        if duration:
            rand_duration = duration * random.uniform(0.9, 1.1)
        else:
            rand_duration = random.uniform(0.4, 0.7)  # Default human-like movement
            
        return rand_x, rand_y, rand_duration
        
    def send_message(self, text):
        """Send a message to the chat input using PyAutoGUI."""
        # Detect chat input
        input_area = self.detect_chat_input()
        if not input_area:
            logging.error("Failed to detect chat input area")
            return False
            
        try:
            # Calculate target with slight randomness
            target_x, target_y, duration = self.add_human_randomness(
                input_area["center_x"], 
                input_area["center_y"],
                0.5
            )
            
            # Move mouse with human-like motion
            logging.info(f"Moving mouse to chat input at ({target_x:.1f}, {target_y:.1f})")
            pyautogui.moveTo(target_x, target_y, duration=duration, tween=pyautogui.easeOutQuad)
            
            # Add small pause before clicking (human behavior)
            time.sleep(random.uniform(0.1, 0.3))
            
            # Click in the input field
            pyautogui.click()
            logging.info("Clicked in chat input field")
            
            # Small pause after clicking
            time.sleep(random.uniform(0.2, 0.5))
            
            # Save original clipboard content
            original_clipboard = pyperclip.paste()
            
            # Copy text to clipboard
            pyperclip.copy(text)
            
            # Paste with keyboard shortcut
            logging.info("Pasting text via clipboard")
            pyautogui.hotkey('command', 'v')  # Assuming macOS, use ctrl+v for Windows
            
            # Wait for paste to complete
            time.sleep(0.5)
            
            # Restore original clipboard
            pyperclip.copy(original_clipboard)
            
            # Take screenshot after pasting
            self.capture_screenshot("after_paste")
            
            # Small pause before pressing enter
            time.sleep(random.uniform(0.3, 0.8))
            
            # Press enter to send
            pyautogui.press('enter')
            logging.info("Pressed Enter to send message")
            
            # Take screenshot after sending
            self.capture_screenshot("after_send")
            
            print(f"Successfully sent message: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            return True
            
        except Exception as e:
            logging.error(f"Error sending message: {e}")
            print(f"Failed to send message: {e}")
            return False
    
    def detect_captcha(self):
        """
        Mock captcha detection using simple heuristics.
        
        For a real implementation, this would need image recognition or 
        OCR to detect CAPTCHA text/elements.
        """
        print("Checking for CAPTCHA...")
        screenshot, _ = self.capture_screenshot("captcha_check")
        
        # For now, we're just going to provide a manual check prompt
        # In a real implementation, this would use OCR to check for CAPTCHA keywords
        response = input("Do you see a CAPTCHA on screen? (y/n): ")
        return response.lower().startswith('y')
    
    def wait_for_captcha_solution(self, timeout=60):
        """Wait for the user to solve a CAPTCHA."""
        print(f"Please solve the CAPTCHA on screen. You have {timeout} seconds.")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            time_passed = int(time.time() - start_time)
            time_left = timeout - time_passed
            print(f"Waiting for CAPTCHA solution... {time_left} seconds left", end="\r")
            
            # Check every 5 seconds if the CAPTCHA is still there
            if time_passed % 5 == 0:
                if not self.detect_captcha():
                    print("\nCAPTCHA appears to be solved!")
                    return True
                    
            time.sleep(1)
            
        print("\nTimeout waiting for CAPTCHA solution")
        return False

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Simple UI Automation for Chat Interfaces")
    
    # Create a group for the query (either positional or with flag)
    query_group = parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument("query", nargs="?", default=None, help="Text to send to chat")
    query_group.add_argument("--query", "--text", dest="query_flag", help="Text to send to chat")
    
    parser.add_argument("--site", choices=["perplexity", "qwen", "generic"], 
                      default="generic", help="Chat site to target")
    parser.add_argument("--timeout", type=int, default=5, 
                      help="Seconds to wait before starting (default: 5)")
    parser.add_argument("--debug", action="store_true", 
                      help="Enable debug mode with screenshots")
    
    args = parser.parse_args()
    
    # If query was provided with flag, use that value
    if args.query_flag:
        args.query = args.query_flag
        
    return args

def get_manual_position():
    """Let the user manually position and then enter the position."""
    print("\nInstructions:")
    print("1. Move your mouse over the chat input field")
    print("2. Note the position in the corner of your screen")
    print("3. Come back to this terminal")
    
    input("\nPress Enter when ready to capture the current mouse position...")
    
    # Get current position
    x, y = pyautogui.position()
    print(f"\nCaptured position: ({x}, {y})")
    
    verify = input("\nIs this position correct? (y/n): ")
    if verify.lower().startswith('y'):
        return x, y
    else:
        print("\nLet's try manual entry...")
        try:
            x_str = input("Enter X coordinate: ")
            y_str = input("Enter Y coordinate: ")
            return int(x_str), int(y_str)
        except ValueError:
            print("Invalid coordinates, will use estimated position")
            return None, None

def main():
    """Main entry point."""
    args = parse_args()
    
    print("\n" + "=" * 60)
    print(f"Simple UI Automation - {args.site.upper()}")
    print("=" * 60)
    print(f"Text to send: {args.query[:50]}{'...' if len(args.query) > 50 else ''}")
    print("=" * 60 + "\n")
    
    # Give user time to switch to target window
    print(f"You have {args.timeout} seconds to switch to the chat window...")
    for i in range(args.timeout, 0, -1):
        print(f"{i}...", end=" ", flush=True)
        time.sleep(1)
    print("\n")
    
    try:
        # Initialize automation
        automation = SimpleUIAutomation(
            site_name=args.site,
            debug=args.debug
        )
        
        # Check for CAPTCHA
        if automation.detect_captcha():
            print("CAPTCHA detected!")
            if not automation.wait_for_captcha_solution():
                print("Failed to get CAPTCHA solution. Exiting.")
                return 1
        
        # Ask user if they want to manually click
        manual_mode = input("Do you want to manually click on the input field? (y/n): ").lower().startswith('y')
        
        if manual_mode:
            # Get manual position
            click_x, click_y = get_manual_position()
            
            # If we got a position, override the detect_chat_input method temporarily
            if click_x is not None and click_y is not None:
                # Create a closure to return the manual position
                def manual_detect():
                    return {
                        "x1": click_x - 100,
                        "y1": click_y - 20,
                        "x2": click_x + 100,
                        "y2": click_y + 20,
                        "width": 200,
                        "height": 40,
                        "center_x": click_x,
                        "center_y": click_y
                    }
                
                # Save original method
                original_detect = automation.detect_chat_input
                
                # Override method
                automation.detect_chat_input = manual_detect
                
                # Send message with manual position
                print("Sending message using manual position...")
                success = automation.send_message(args.query)
                
                # Restore original method
                automation.detect_chat_input = original_detect
            else:
                # Fallback to automatic
                print("No manual position detected, falling back to automatic...")
                success = automation.send_message(args.query)
        else:
            # Use automatic detection
            print("Sending message...")
            success = automation.send_message(args.query)
        
        if success:
            print("\nMessage sent successfully!")
        else:
            print("\nFailed to send message.")
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation canceled by user.")
        return 1
    except Exception as e:
        logging.exception("Unhandled exception")
        print(f"\nError: {e}")
        return 1
        
    print("\nDone!")
    return 0

if __name__ == "__main__":
    sys.exit(main())