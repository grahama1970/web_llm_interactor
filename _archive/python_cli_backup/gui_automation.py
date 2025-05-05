#!/usr/bin/env python3
"""
AI Chat Access - GUI Automation Approach
This script uses OS-level GUI automation rather than browser automation
to interact with AI chat sites, making it much harder to detect as a bot.
"""

import sys
import time
import random
import argparse
import subprocess
import pyautogui
import pyperclip
from PIL import Image, ImageGrab
import pytesseract  # For OCR to read screen text
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("gui_automation.log"),
        logging.StreamHandler()
    ]
)

# Add human-like behavior
def human_type(text, min_delay=0.05, max_delay=0.2):
    """Type text with human-like random delays between keystrokes"""
    for char in text:
        pyautogui.write(char)
        # Random delay between keystrokes
        time.sleep(random.uniform(min_delay, max_delay))

def human_move(x, y, duration=None):
    """Move mouse to position with human-like movement"""
    if duration is None:
        # Randomize movement duration based on distance
        current_x, current_y = pyautogui.position()
        distance = ((x - current_x) ** 2 + (y - current_y) ** 2) ** 0.5
        duration = random.uniform(0.5, 1.0) * (distance / 500)
        
    # Use pyautogui's built-in easing functions for more natural movement
    pyautogui.moveTo(x, y, duration=duration, tween=pyautogui.easeOutQuad)

def random_mouse_movement():
    """Make random mouse movements to appear human"""
    current_x, current_y = pyautogui.position()
    offset_x = random.randint(-100, 100)
    offset_y = random.randint(-100, 100)
    human_move(current_x + offset_x, current_y + offset_y)
    time.sleep(random.uniform(0.1, 0.3))
    # Move back
    human_move(current_x, current_y)

def scroll_random():
    """Scroll a random amount"""
    scroll_amount = random.randint(-300, 300)
    pyautogui.scroll(scroll_amount)
    time.sleep(random.uniform(0.5, 1.5))

def is_captcha_present():
    """Check if a CAPTCHA is present on screen"""
    # Take screenshot
    screenshot = ImageGrab.grab()
    
    # Use OCR to read text in the screenshot
    text = pytesseract.image_to_string(screenshot).lower()
    
    # Keywords that might indicate a CAPTCHA
    captcha_keywords = [
        'captcha', 'robot', 'human', 'verify', 'challenge', 
        'security check', 'not a robot', 'puzzles'
    ]
    
    for keyword in captcha_keywords:
        if keyword in text:
            logging.info(f"CAPTCHA detected: found '{keyword}' on screen")
            return True
    
    return False

def find_and_click_image(image_path, confidence=0.7, max_attempts=3):
    """Find and click on an image on screen"""
    attempts = 0
    while attempts < max_attempts:
        try:
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if location:
                human_move(location.x, location.y)
                time.sleep(random.uniform(0.1, 0.3))
                pyautogui.click()
                return True
            else:
                logging.info(f"Image {image_path} not found on attempt {attempts+1}")
        except Exception as e:
            logging.error(f"Error finding image: {e}")
        
        attempts += 1
        time.sleep(1)
    
    return False

def open_browser(url):
    """Open the default browser with the specified URL"""
    if sys.platform == 'darwin':  # macOS
        subprocess.run(['open', url])
    elif sys.platform == 'win32':  # Windows
        subprocess.run(['start', url], shell=True)
    else:  # Linux
        subprocess.run(['xdg-open', url])
    
    # Wait for browser to open
    time.sleep(5)

def interact_with_qwen():
    """Interact with chat.qwen.ai"""
    logging.info("Starting interaction with chat.qwen.ai")
    
    # Open browser with Qwen
    open_browser("https://chat.qwen.ai/")
    logging.info("Browser opened with chat.qwen.ai")
    
    # Wait for page to load
    time.sleep(5)
    
    # Check for CAPTCHA
    if is_captcha_present():
        logging.info("CAPTCHA detected - waiting for manual resolution")
        input("Please solve the CAPTCHA manually and press Enter when ready...")
    
    # Try to find and click on input field using image recognition
    # You would need to create a screenshot of the Qwen input field
    input_field_found = find_and_click_image('qwen_input.png')
    
    if not input_field_found:
        logging.error("Could not find input field")
        return False
    
    # Type question with human-like timing
    question = "What are the latest advancements in quantum computing?"
    human_type(question)
    time.sleep(random.uniform(0.5, 1.5))
    
    # Press Enter to submit
    pyautogui.press('enter')
    
    # Wait for response
    logging.info("Waiting for response...")
    time.sleep(15)
    
    # Take screenshot of the response
    screenshot = ImageGrab.grab()
    screenshot.save('qwen_response.png')
    logging.info("Screenshot saved to qwen_response.png")
    
    # Try to select and copy text from response
    # This is OS-specific and might need adjustment
    pyautogui.hotkey('command', 'a')  # Select all on Mac
    time.sleep(0.5)
    pyautogui.hotkey('command', 'c')  # Copy on Mac
    
    # Get the copied text
    response_text = pyperclip.paste()
    
    # Save response text
    with open('qwen_response.txt', 'w') as f:
        f.write(response_text)
    
    logging.info("Interaction completed")
    return True

def interact_with_perplexity():
    """Interact with perplexity.ai"""
    logging.info("Starting interaction with perplexity.ai")
    
    # Open browser with Perplexity
    open_browser("https://www.perplexity.ai/")
    logging.info("Browser opened with perplexity.ai")
    
    # Wait for page to load
    time.sleep(5)
    
    # Check for CAPTCHA
    if is_captcha_present():
        logging.info("CAPTCHA detected - waiting for manual resolution")
        input("Please solve the CAPTCHA manually and press Enter when ready...")
    
    # Try to find and click on input field using image recognition
    # You would need to create a screenshot of the Perplexity input field
    input_field_found = find_and_click_image('perplexity_input.png')
    
    if not input_field_found:
        logging.error("Could not find input field")
        return False
    
    # Type question with human-like timing
    question = "What are the latest advancements in quantum computing?"
    human_type(question)
    time.sleep(random.uniform(0.5, 1.5))
    
    # Press Enter to submit
    pyautogui.press('enter')
    
    # Wait for response
    logging.info("Waiting for response...")
    time.sleep(15)
    
    # Take screenshot of the response
    screenshot = ImageGrab.grab()
    screenshot.save('perplexity_response.png')
    logging.info("Screenshot saved to perplexity_response.png")
    
    # Try to select and copy text from response
    # This is OS-specific and might need adjustment
    pyautogui.hotkey('command', 'a')  # Select all on Mac
    time.sleep(0.5)
    pyautogui.hotkey('command', 'c')  # Copy on Mac
    
    # Get the copied text
    response_text = pyperclip.paste()
    
    # Save response text
    with open('perplexity_response.txt', 'w') as f:
        f.write(response_text)
    
    logging.info("Interaction completed")
    return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI Chat GUI Automation")
    parser.add_argument("--site", choices=["qwen", "perplexity"], default="qwen",
                      help="Which site to interact with")
    parser.add_argument("--question", type=str, 
                      help="Question to ask the AI")
    
    args = parser.parse_args()
    
    # Create screenshots folder if it doesn't exist
    subprocess.run(['mkdir', '-p', 'screenshots'])
    
    # Get screen size
    screen_width, screen_height = pyautogui.size()
    logging.info(f"Screen resolution: {screen_width}x{screen_height}")
    
    # Fail-safe (move mouse to upper-left to abort)
    pyautogui.FAILSAFE = True
    
    try:
        if args.site == "qwen":
            interact_with_qwen()
        else:
            interact_with_perplexity()
    except KeyboardInterrupt:
        logging.info("Script interrupted by user")
    except Exception as e:
        logging.error(f"Error: {e}")
    
    logging.info("Script completed")

if __name__ == "__main__":
    main()