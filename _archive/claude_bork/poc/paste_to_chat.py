#!/usr/bin/env python3
"""
Proof of Concept: Text Pasting to Chat Input with Qwen-VL

This script demonstrates detecting a chat input field with Qwen-VL and then
pasting text into it. This bypasses traditional browser automation by using
PyAutoGUI to simulate real mouse and keyboard interaction at the OS level.

Usage:
  1. Open the target website in your browser
  2. Run this script with a query: python paste_to_chat.py "Your question here"
  3. The script will detect the chat input field and paste your text
  4. Screenshots will be saved in the debug directory

Note: This script requires PyTorch, transformers, and the Qwen-VL model to be installed.
"""

import os
import sys
import json
import time
import argparse
import platform
import logging
import random
import pyperclip
from PIL import Image, ImageDraw
import pyautogui

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Configure PyAutoGUI
pyautogui.FAILSAFE = True  # Move mouse to top-left to abort
pyautogui.PAUSE = 0.5  # Small pause between actions

# Create debug directory
DEBUG_DIR = "debug"
os.makedirs(DEBUG_DIR, exist_ok=True)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Chat Input Paste Test")
    
    # Create a group for the query (either positional or with flag)
    query_group = parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument("query", nargs="?", default=None, help="Text to paste into the chat input field")
    query_group.add_argument("--query", "--text", dest="query_flag", help="Text to paste into the chat input field (alternative to positional argument)")
    
    parser.add_argument("--timeout", type=int, default=5, 
                       help="Seconds to wait before starting (default: 5)")
    parser.add_argument("--model", type=str, default="Qwen/Qwen-VL-Chat",
                       help="Qwen-VL model to use (default: Qwen-VL-Chat)")
    parser.add_argument("--debug", action="store_true", help="Enable extra debug screenshots")
    
    args = parser.parse_args()
    
    # If query was provided with flag, use that value
    if args.query_flag:
        args.query = args.query_flag
        
    return args

def check_and_setup_device():
    """Check and setup the appropriate device (MPS, CUDA, or CPU)."""
    try:
        import torch
        
        # Check device availability
        device = None
        device_type = "cpu"  # Default fallback
        
        # Try to check for MPS, but handle potential attribute errors on older PyTorch
        has_mps = False
        try:
            has_mps = hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()
        except AttributeError:
            pass
            
        if has_mps:
            device_type = "mps"
            device = torch.device("mps")
            logging.info("Using MPS acceleration!")
            
        # Check for CUDA (NVIDIA GPUs)
        elif torch.cuda.is_available():
            device_type = "cuda"
            device = torch.device("cuda")
            logging.info("Using CUDA acceleration!")
            
        else:
            device = torch.device("cpu")
            logging.info("Using CPU (no GPU acceleration available)")
            
            # Provide additional info for Mac Intel users
            if platform.system() == 'Darwin' and platform.machine() == 'x86_64':
                logging.info("==================================================")
                logging.info("INFO: Intel Mac detected.")
                logging.info("You appear to be using PyTorch without MPS support.")
                logging.info("This is expected on Intel Macs with official PyTorch.")
                logging.info("==================================================")
        
        return device, device_type
    
    except ImportError:
        logging.error("PyTorch not installed. Please run the fix_torch.py script first.")
        sys.exit(1)

def load_vision_models(model_name, device):
    """Load Qwen-VL models with appropriate error handling."""
    try:
        from transformers import AutoProcessor, AutoModelForCausalLM
        
        logging.info(f"Loading Qwen-VL model: {model_name}")
        
        # Load model and processor
        model = AutoModelForCausalLM.from_pretrained(model_name)
        processor = AutoProcessor.from_pretrained(model_name)
        
        # Move model to device
        model = model.to(device)
        logging.info(f"Model loaded and moved to {device}")
        
        return model, processor
    
    except ImportError:
        logging.error("Transformers not installed. Install with: pip install transformers")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to load Qwen-VL model: {e}")
        sys.exit(1)

def capture_and_save_screenshot(prefix="screenshot"):
    """Capture screenshot and save it."""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    screenshot = pyautogui.screenshot()
    filepath = os.path.join(DEBUG_DIR, f"{prefix}_{timestamp}.png")
    screenshot.save(filepath)
    logging.info(f"Saved {prefix} to {filepath}")
    return screenshot, filepath

def detect_chat_input(model, processor, device, screenshot=None):
    """Detect chat input field using Qwen-VL."""
    logging.info("Detecting chat input field...")
    
    # Capture screenshot if not provided
    if screenshot is None:
        screenshot, _ = capture_and_save_screenshot("detect")
    
    # Prepare prompt for detection
    prompt = (
        "Identify the chat input field (textarea or text box where users type messages) "
        "in the screenshot. Return the bounding box coordinates as JSON with "
        "{'top_left': [x, y], 'bottom_right': [x, y]}."
    )
    
    # Process screenshot with vision model
    inputs = processor(text=prompt, images=[screenshot], return_tensors="pt")
    
    # Move inputs to the correct device
    for key in inputs:
        if isinstance(inputs[key], torch.Tensor):
            inputs[key] = inputs[key].to(device)
    
    # Generate output
    outputs = model.generate(**inputs, max_new_tokens=100)
    response = processor.decode(outputs[0], skip_special_tokens=True)
    
    try:
        # Try to parse JSON response
        result = json.loads(response)
        if "top_left" in result and "bottom_right" in result:
            x1, y1 = result["top_left"]
            x2, y2 = result["bottom_right"]
            width = x2 - x1
            height = y2 - y1
            logging.info(f"Detection success: {width}x{height} pixels at ({x1}, {y1})")
            
            # Process coordinates
            bbox = {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "width": width,
                "height": height,
                "center_x": x1 + width // 2,
                "center_y": y1 + height // 2
            }
            return bbox
        else:
            logging.error(f"Missing coordinates in response: {result}")
            return None
    except json.JSONDecodeError:
        logging.error(f"Failed to parse response as JSON: {response}")
        return None

def add_human_randomness(x, y, duration=None):
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

def paste_text_to_chat(bbox, text, with_clipboard=True):
    """Paste text into a detected chat input field."""
    if not bbox:
        logging.error("Cannot paste: No chat input coordinates")
        return False
        
    # Calculate target coordinates with slight randomness
    target_x, target_y, duration = add_human_randomness(
        bbox["center_x"], 
        bbox["center_y"],
        0.5
    )
    
    # Move mouse with human-like motion (non-linear)
    logging.info(f"Moving mouse to chat input at ({target_x:.1f}, {target_y:.1f})")
    pyautogui.moveTo(target_x, target_y, duration=duration, tween=pyautogui.easeOutQuad)
    
    # Add small pause before clicking (human behavior)
    time.sleep(random.uniform(0.1, 0.3))
    
    # Click into the input field
    pyautogui.click()
    logging.info("Clicked in chat input")
    
    # Add small pause after clicking (human behavior)
    time.sleep(random.uniform(0.2, 0.5))
    
    # Method 1: Copy to clipboard and paste (faster for long text)
    if with_clipboard:
        # Save original clipboard content
        original_clipboard = pyperclip.paste()
        
        # Copy text to clipboard
        pyperclip.copy(text)
        
        # Paste using keyboard shortcut
        logging.info("Pasting text via clipboard")
        if platform.system() == 'Darwin':  # macOS
            pyautogui.hotkey('command', 'v')
        else:  # Windows/Linux
            pyautogui.hotkey('ctrl', 'v')
            
        # Restore original clipboard (good practice)
        time.sleep(0.5)
        pyperclip.copy(original_clipboard)
    
    # Method 2: Type the text directly (more human-like, but slower)
    else:
        logging.info("Typing text character by character")
        pyautogui.write(text, interval=random.uniform(0.05, 0.15))  # Human-like typing speed
    
    # Capture screenshot after pasting
    screenshot, _ = capture_and_save_screenshot("after_paste")
    
    # Add slight delay before pressing enter (human behavior)
    time.sleep(random.uniform(0.3, 0.8))
    
    return True

def send_message(text):
    """Press Enter to send the message."""
    logging.info("Pressing Enter to send message")
    pyautogui.press('enter')
    
    # Capture screenshot after sending
    screenshot, _ = capture_and_save_screenshot("after_send")
    time.sleep(1)  # Brief pause to ensure screenshot captures result
    
    return True

def main():
    """Main function."""
    # Parse arguments
    args = parse_args()
    
    print("\n" + "=" * 60)
    print("Chat Input Detection & Paste - Proof of Concept")
    print("=" * 60)
    print(f"Text to paste: \"{args.query}\"")
    print("=" * 60 + "\n")
    
    # Setup
    device, device_type = check_and_setup_device()
    
    # This import is placed here to ensure it happens after device setup
    import torch
    
    # Load models
    model, processor = load_vision_models(args.model, device)
    
    # Wait for user to switch to correct window
    print(f"\nMake sure the target website is visible.")
    print(f"You have {args.timeout} seconds to switch to the browser window...")
    for i in range(args.timeout, 0, -1):
        print(f"{i}...", end=" ", flush=True)
        time.sleep(1)
    print("\n")
    
    try:
        # Capture initial screenshot
        screenshot, _ = capture_and_save_screenshot("detect")
        
        # Detect chat input field
        bbox = detect_chat_input(model, processor, device, screenshot)
        
        if not bbox:
            print("\n" + "=" * 60)
            print("ERROR: Could not detect chat input field!")
            print("=" * 60 + "\n")
            return 1
            
        # Paste text to the detected input field
        print("\nDetected chat input field, pasting text...")
        success = paste_text_to_chat(bbox, args.query)
        
        if not success:
            print("\n" + "=" * 60)
            print("ERROR: Failed to paste text to chat input!")
            print("=" * 60 + "\n")
            return 1
            
        # Send the message
        print("\nText pasted successfully, sending message...")
        send_message(args.query)
        
        print("\n" + "=" * 60)
        print("SUCCESS: Text has been sent to the chat!")
        print("=" * 60 + "\n")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        logging.exception("Unhandled exception")
        print(f"\nError: {e}")
        
    print("Done!")
    return 0

if __name__ == "__main__":
    sys.exit(main())