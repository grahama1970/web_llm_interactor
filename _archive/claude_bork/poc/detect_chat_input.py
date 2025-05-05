#!/usr/bin/env python3
"""
Proof of Concept: Chat Input Detection with Qwen-VL

This script demonstrates the core capability of detecting the chat input field
in a web browser using Qwen-VL vision model and screenshots. This is a focused
test script that only tests the detection capability.

Usage:
  1. Open the target website in your browser
  2. Run this script
  3. The script will take a screenshot and attempt to identify the chat input field
  4. Results will be displayed with bounding box coordinates

Note: This script requires PyTorch, transformers, and the Qwen-VL model to be installed.
"""

import os
import sys
import json
import time
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

def load_vision_models(device):
    """Load Qwen-VL models with appropriate error handling."""
    try:
        from transformers import AutoProcessor, AutoModelForCausalLM
        
        model_name = "Qwen/Qwen-VL-Chat"
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

def capture_and_save_screenshot():
    """Capture screenshot and save it."""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    screenshot = pyautogui.screenshot()
    filepath = os.path.join(DEBUG_DIR, f"detect_{timestamp}.png")
    screenshot.save(filepath)
    logging.info(f"Saved screenshot to {filepath}")
    return screenshot, filepath

def detect_chat_input(model, processor, device, screenshot):
    """Detect chat input field using Qwen-VL."""
    logging.info("Detecting chat input field...")
    
    # Prepare prompt for detection
    prompt = (
        "Identify the chat input field (textarea or text box where users type messages) "
        "in the screenshot. Return the bounding box coordinates as JSON with "
        "{'top_left': [x, y], 'bottom_right': [x, y]}."
    )
    
    # Process screenshot
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
        logging.info(f"Detection result: {result}")
        return result
    except json.JSONDecodeError:
        logging.error(f"Failed to parse response as JSON: {response}")
        return None

def visualize_detection(screenshot, bbox_data, output_path=None):
    """Draw bounding box on screenshot for visualization."""
    if not bbox_data or "top_left" not in bbox_data or "bottom_right" not in bbox_data:
        logging.error("Invalid bounding box data for visualization")
        return
    
    # Make a copy of the screenshot
    image = screenshot.copy()
    draw = ImageDraw.Draw(image)
    
    # Extract coordinates
    x1, y1 = bbox_data["top_left"]
    x2, y2 = bbox_data["bottom_right"]
    
    # Draw rectangle
    draw.rectangle([(x1, y1), (x2, y2)], outline="red", width=3)
    
    # Save output
    if not output_path:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        output_path = os.path.join(DEBUG_DIR, f"detected_chat_input_{timestamp}.png")
    
    image.save(output_path)
    logging.info(f"Saved visualization to {output_path}")
    return output_path

def main():
    """Main function."""
    print("\n" + "=" * 60)
    print("Chat Input Detection - Qwen-VL Proof of Concept")
    print("=" * 60 + "\n")
    
    # Setup
    device, device_type = check_and_setup_device()
    
    # This import is placed here to ensure it happens after device setup
    import torch
    
    # Load models
    model, processor = load_vision_models(device)
    
    # Wait for user to switch to correct window
    print("\nMake sure the target website is visible.")
    print("You have 5 seconds to switch to the browser window...")
    for i in range(5, 0, -1):
        print(f"{i}...", end=" ", flush=True)
        time.sleep(1)
    print("\n")
    
    # Capture screenshot
    screenshot, screenshot_path = capture_and_save_screenshot()
    
    # Detect chat input
    result = detect_chat_input(model, processor, device, screenshot)
    
    if result and "top_left" in result and "bottom_right" in result:
        # Success - visualize the result
        x1, y1 = result["top_left"]
        x2, y2 = result["bottom_right"]
        width = x2 - x1
        height = y2 - y1
        print("\n" + "=" * 60)
        print("SUCCESS: Chat input field detected!")
        print(f"Position: ({x1}, {y1}) to ({x2}, {y2})")
        print(f"Size: {width}x{height} pixels")
        print("=" * 60 + "\n")
        
        # Create visualization
        vis_path = visualize_detection(screenshot, result)
        print(f"Screenshot with detected input field saved to: {vis_path}")
    else:
        print("\n" + "=" * 60)
        print("FAILED: Could not detect chat input field")
        print("=" * 60 + "\n")
    
    print("Done!")

if __name__ == "__main__":
    main()