#!/usr/bin/env python3
"""
Proof of Concept: CAPTCHA Detection with Qwen-VL

This script demonstrates the ability to detect CAPTCHA challenges on AI chat websites
using Qwen-VL vision model. The script takes a screenshot and analyzes it to determine
if a CAPTCHA is present, allowing automation to pause and wait for human intervention.

Usage:
  1. Open the target website that may display a CAPTCHA
  2. Run this script
  3. The script will report if it detects a CAPTCHA challenge

Note: This script requires PyTorch, transformers, and the Qwen-VL model to be installed.
"""

import os
import sys
import time
import argparse
import platform
import logging
from PIL import Image, ImageDraw
import pyautogui

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Create debug directory
DEBUG_DIR = "debug"
os.makedirs(DEBUG_DIR, exist_ok=True)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="CAPTCHA Detection Test")
    parser.add_argument("--timeout", type=int, default=5, 
                       help="Seconds to wait before starting (default: 5)")
    parser.add_argument("--model", type=str, default="Qwen/Qwen-VL-Chat",
                       help="Qwen-VL model to use (default: Qwen-VL-Chat)")
    parser.add_argument("--wait", type=int, default=0,
                       help="Seconds to wait for manual CAPTCHA solution (0=don't wait)")
    parser.add_argument("--monitor", action="store_true", 
                       help="Continuously monitor for CAPTCHA presence")
    return parser.parse_args()

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

def capture_and_save_screenshot(prefix="captcha_check"):
    """Capture screenshot and save it."""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    screenshot = pyautogui.screenshot()
    filepath = os.path.join(DEBUG_DIR, f"{prefix}_{timestamp}.png")
    screenshot.save(filepath)
    logging.info(f"Saved {prefix} to {filepath}")
    return screenshot, filepath

def detect_captcha(model, processor, device, screenshot=None):
    """Detect CAPTCHA presence using Qwen-VL."""
    logging.info("Checking for CAPTCHA...")
    
    # Capture screenshot if not provided
    if screenshot is None:
        screenshot, _ = capture_and_save_screenshot()
    
    # Prepare prompt for detection - several variants for robustness
    prompt = (
        "Is there a CAPTCHA challenge visible in this screenshot? Look for:"
        "1. 'Select all images with...' challenges"
        "2. 'I am not a robot' checkboxes"
        "3. Slider puzzles or image recognition challenges"
        "4. Text asking to solve a puzzle to continue"
        "Answer only 'Yes' or 'No'."
    )
    
    try:
        # Process screenshot with vision model
        import torch
        inputs = processor(text=prompt, images=[screenshot], return_tensors="pt")
        
        # Move inputs to the correct device
        for key in inputs:
            if isinstance(inputs[key], torch.Tensor):
                inputs[key] = inputs[key].to(device)
        
        # Generate output
        outputs = model.generate(**inputs, max_new_tokens=50)
        response = processor.decode(outputs[0], skip_special_tokens=True).strip().lower()
        
        # Check if response indicates CAPTCHA presence
        is_captcha = False
        if "yes" in response or "captcha" in response:
            is_captcha = True
            logging.info("CAPTCHA DETECTED!")
        else:
            logging.info("No CAPTCHA detected")
            
        return is_captcha, response
        
    except Exception as e:
        logging.error(f"Error detecting CAPTCHA: {e}")
        return False, f"Error: {str(e)}"

def wait_for_captcha_solution(model, processor, device, timeout=60):
    """Wait for CAPTCHA to be resolved manually."""
    if timeout <= 0:
        return False
        
    logging.info(f"Waiting up to {timeout} seconds for manual CAPTCHA solution...")
    print("\n" + "=" * 60)
    print("CAPTCHA detected! Please solve it manually.")
    print(f"This script will check every 5 seconds for up to {timeout} seconds.")
    print("=" * 60 + "\n")
    
    start_time = time.time()
    check_interval = 5  # Check every 5 seconds
    
    while time.time() - start_time < timeout:
        # Calculate time elapsed and remaining
        elapsed = time.time() - start_time
        remaining = timeout - elapsed
        
        print(f"Waiting... {elapsed:.0f}s elapsed, {remaining:.0f}s remaining")
        time.sleep(check_interval)
        
        # Check if CAPTCHA is still present
        is_captcha, _ = detect_captcha(model, processor, device)
        if not is_captcha:
            print("\n" + "=" * 60)
            print("CAPTCHA SOLVED! Continuing...")
            print("=" * 60 + "\n")
            return True
            
    print("\n" + "=" * 60)
    print("TIMEOUT: CAPTCHA solution waiting period expired")
    print("=" * 60 + "\n")
    return False

def monitor_for_captcha(model, processor, device, interval=10):
    """Continuously monitor for CAPTCHA appearance."""
    print("\n" + "=" * 60)
    print("CAPTCHA Monitoring Mode Activated")
    print(f"Checking every {interval} seconds. Press Ctrl+C to stop.")
    print("=" * 60 + "\n")
    
    try:
        check_count = 0
        while True:
            check_count += 1
            print(f"Check #{check_count} - ", end="", flush=True)
            
            is_captcha, response = detect_captcha(model, processor, device)
            
            if is_captcha:
                print("CAPTCHA DETECTED!")
                print("\n" + "=" * 60)
                print("ALERT: CAPTCHA detected on screen!")
                print("Response: " + response)
                print("=" * 60 + "\n")
                
                # Make a sound alert if on macOS
                if platform.system() == 'Darwin':
                    os.system('say "Captcha detected"')
                    
                # Wait before next check
                print(f"Waiting {interval*2} seconds before next check...")
                time.sleep(interval * 2)  # Wait longer after detection
            else:
                print("No CAPTCHA detected.")
                time.sleep(interval)
                
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")
        return

def main():
    """Main function."""
    # Parse arguments
    args = parse_args()
    
    print("\n" + "=" * 60)
    print("CAPTCHA Detection - Qwen-VL Proof of Concept")
    print("=" * 60 + "\n")
    
    # Setup
    device, device_type = check_and_setup_device()
    
    # This import is placed here to ensure it happens after device setup
    import torch
    
    # Load models
    model, processor = load_vision_models(args.model, device)
    
    # Wait for user to switch to correct window
    if not args.monitor:
        print(f"\nMake sure the target website is visible.")
        print(f"You have {args.timeout} seconds to switch to the browser window...")
        for i in range(args.timeout, 0, -1):
            print(f"{i}...", end=" ", flush=True)
            time.sleep(1)
        print("\n")
    
    try:
        if args.monitor:
            # Run in continuous monitoring mode
            monitor_for_captcha(model, processor, device)
        else:
            # Single check mode
            screenshot, _ = capture_and_save_screenshot()
            is_captcha, response = detect_captcha(model, processor, device, screenshot)
            
            if is_captcha:
                print("\n" + "=" * 60)
                print("CAPTCHA DETECTED!")
                print(f"Response: {response}")
                print("=" * 60 + "\n")
                
                # Wait for manual solution if requested
                if args.wait > 0:
                    wait_for_captcha_solution(model, processor, device, args.wait)
            else:
                print("\n" + "=" * 60)
                print("No CAPTCHA detected")
                print(f"Response: {response}")
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