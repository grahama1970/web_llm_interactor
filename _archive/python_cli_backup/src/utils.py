#!/usr/bin/env python3
"""
Utility functions for AI chat automation
"""

import os
import sys
import time
import logging
import random
import numpy as np
import pyautogui
import pyperclip
from PIL import Image, ImageGrab
import pytesseract
from typing import List, Tuple, Optional, Union, Dict, Any

# Try to import from local directory first, then from examples
try:
    from .image_processing_utils import compress_image, compress_image_object
except ImportError:
    try:
        # Also try importing from examples directory
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'examples'))
        from image_processing_utils import compress_image, compress_image_object
    except ImportError:
        logging.warning("Could not import image_processing_utils, image compression will be disabled")
        compress_image = None
        compress_image_object = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("utils.log"),
        logging.StreamHandler()
    ]
)

def find_image_on_screen(
    image_path: str,
    confidence: float = 0.8,
    grayscale: bool = False,
    region: Optional[Tuple[int, int, int, int]] = None
) -> Optional[Tuple[int, int]]:
    """
    Find an image on screen and return its center coordinates
    
    Args:
        image_path: Path to the image file to find
        confidence: Minimum confidence level (0-1)
        grayscale: Whether to convert screenshots to grayscale
        region: Optional search region (left, top, width, height)
        
    Returns:
        (x, y) coordinates of center of found image, or None if not found
    """
    try:
        location = pyautogui.locateCenterOnScreen(
            image_path, 
            confidence=confidence,
            grayscale=grayscale,
            region=region
        )
        
        if location:
            logging.info(f"Found image {os.path.basename(image_path)} at {location}")
        else:
            logging.info(f"Image {os.path.basename(image_path)} not found on screen")
            
        return location
    except Exception as e:
        logging.error(f"Error finding image {image_path}: {e}")
        return None

def wait_for_image(
    image_path: str,
    timeout: int = 30,
    check_interval: float = 1.0,
    confidence: float = 0.8,
    grayscale: bool = False,
    region: Optional[Tuple[int, int, int, int]] = None
) -> Optional[Tuple[int, int]]:
    """
    Wait for an image to appear on screen
    
    Args:
        image_path: Path to the image file to find
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds
        confidence: Minimum confidence level (0-1)
        grayscale: Whether to convert screenshots to grayscale
        region: Optional search region (left, top, width, height)
        
    Returns:
        (x, y) coordinates of center of found image, or None if timeout
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        location = find_image_on_screen(
            image_path, 
            confidence=confidence,
            grayscale=grayscale,
            region=region
        )
        
        if location:
            return location
        
        # Wait before next check with slight randomization
        time.sleep(check_interval * random.uniform(0.8, 1.2))
    
    logging.warning(f"Timed out waiting for image {image_path}")
    return None

def read_text_from_region(
    region: Optional[Tuple[int, int, int, int]] = None,
    lang: str = 'eng'
) -> str:
    """
    Read text from a screen region using OCR
    
    Args:
        region: Screen region to capture (left, top, width, height)
              If None, captures the entire screen
        lang: Language for OCR (default: English)
        
    Returns:
        Extracted text as string
    """
    try:
        # Take screenshot
        screenshot = ImageGrab.grab(bbox=region)
        
        # Use OCR to extract text
        text = pytesseract.image_to_string(screenshot, lang=lang)
        
        # Debug: save the captured region
        debug_dir = "debug"
        os.makedirs(debug_dir, exist_ok=True)
        timestamp = int(time.time())
        debug_path = os.path.join(debug_dir, f"ocr_region_{timestamp}.png")
        screenshot.save(debug_path)
        
        logging.info(f"Read text from region, saved debug image to {debug_path}")
        return text.strip()
    except Exception as e:
        logging.error(f"Error reading text from region: {e}")
        return ""

def find_text_on_screen(
    text: str,
    region: Optional[Tuple[int, int, int, int]] = None,
    case_sensitive: bool = False
) -> bool:
    """
    Check if specific text appears on screen using OCR
    
    Args:
        text: Text to find
        region: Optional screen region to search
        case_sensitive: Whether to perform case-sensitive matching
        
    Returns:
        True if text is found, False otherwise
    """
    screen_text = read_text_from_region(region)
    
    if not case_sensitive:
        return text.lower() in screen_text.lower()
    else:
        return text in screen_text

def save_screenshot(
    filename: Optional[str] = None,
    directory: str = "screenshots",
    region: Optional[Tuple[int, int, int, int]] = None,
    compress: bool = True,
    max_size_kb: int = 500
) -> str:
    """
    Save a screenshot with optional compression
    
    Args:
        filename: Optional filename (default: timestamp)
        directory: Directory to save screenshots
        region: Optional region to capture
        compress: Whether to compress the image (default: True)
        max_size_kb: Maximum size for compressed images in KB
        
    Returns:
        Path to saved screenshot
    """
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = int(time.time())
        filename = f"screenshot_{timestamp}.png"
    
    # Ensure filename has .png extension
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        filename += '.png'
    
    # Full path to save
    filepath = os.path.join(directory, filename)
    
    # Capture screenshot
    screenshot = ImageGrab.grab(bbox=region)
    
    # Try to compress the image directly if requested
    if compress and compress_image_object:
        try:
            # Use direct compression without saving the uncompressed file first
            compressed_filepath = compress_image_object(
                screenshot, 
                directory, 
                os.path.splitext(os.path.basename(filepath))[0], 
                max_size_kb
            )
            
            if compressed_filepath and os.path.exists(compressed_filepath):
                logging.info(f"Directly compressed screenshot saved to {compressed_filepath}")
                return compressed_filepath
        except Exception as e:
            logging.warning(f"Direct image compression failed: {e}")
    
    # Save the original screenshot
    screenshot.save(filepath)
    
    # Try to compress the saved file if requested
    if compress and compress_image:
        try:
            compressed_path = compress_image(filepath, directory, max_size_kb)
            
            if compressed_path and compressed_path != filepath and os.path.exists(compressed_path):
                # Remove the original file if compression succeeded
                os.remove(filepath)
                logging.info(f"Compressed screenshot from {filepath} to {compressed_path}")
                return compressed_path
        except Exception as e:
            logging.error(f"Error compressing screenshot: {e}")
            # If compression fails, use the original image
    
    logging.info(f"Saved screenshot to {filepath}")
    return filepath

def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to clipboard
    
    Args:
        text: Text to copy
        
    Returns:
        True on success, False on failure
    """
    try:
        pyperclip.copy(text)
        return True
    except Exception as e:
        logging.error(f"Error copying to clipboard: {e}")
        return False

def get_clipboard_text() -> str:
    """
    Get text from clipboard
    
    Returns:
        Text from clipboard or empty string on failure
    """
    try:
        return pyperclip.paste()
    except Exception as e:
        logging.error(f"Error getting clipboard text: {e}")
        return ""

def is_point_in_rect(
    point: Tuple[int, int],
    rect: Tuple[int, int, int, int]
) -> bool:
    """
    Check if a point is inside a rectangle
    
    Args:
        point: (x, y) coordinates
        rect: (left, top, width, height) of rectangle
        
    Returns:
        True if point is inside rectangle
    """
    x, y = point
    left, top, width, height = rect
    return (left <= x <= left + width) and (top <= y <= top + height)

def calculate_text_region(
    font_size: int,
    char_count: int,
    width_ratio: float = 0.8,
    center_x: Optional[int] = None,
    center_y: Optional[int] = None
) -> Tuple[int, int, int, int]:
    """
    Calculate the approximate region that would contain text
    
    Args:
        font_size: Approximate font size in pixels
        char_count: Number of characters in text
        width_ratio: What portion of screen width to use
        center_x, center_y: Optional center position
        
    Returns:
        (left, top, width, height) region
    """
    # Get screen dimensions
    screen_width, screen_height = pyautogui.size()
    
    # Calculate width based on char count and font size
    # Assume average character is 0.6 * font_size wide
    text_width = min(char_count * font_size * 0.6, screen_width * width_ratio)
    
    # Height based on font size and word wrapping
    chars_per_line = int(text_width / (font_size * 0.6))
    lines = max(1, char_count / chars_per_line)
    text_height = lines * font_size * 1.5  # 1.5 line spacing
    
    # Calculate center position if not provided
    if center_x is None:
        center_x = screen_width // 2
    if center_y is None:
        center_y = screen_height // 2
    
    # Calculate rectangle
    left = max(0, center_x - text_width // 2)
    top = max(0, center_y - text_height // 2)
    
    return (int(left), int(top), int(text_width), int(text_height))

def compare_images(
    image1_path: str,
    image2_path: str,
    threshold: float = 0.95
) -> float:
    """
    Compare two images and return similarity score
    
    Args:
        image1_path: Path to first image
        image2_path: Path to second image
        threshold: Similarity threshold for match
        
    Returns:
        Similarity score between 0 and 1
    """
    try:
        img1 = Image.open(image1_path).convert('L')  # Convert to grayscale
        img2 = Image.open(image2_path).convert('L')
        
        # Resize to same dimensions if different
        if img1.size != img2.size:
            img2 = img2.resize(img1.size)
        
        # Convert to numpy arrays
        arr1 = np.array(img1)
        arr2 = np.array(img2)
        
        # Calculate normalized cross-correlation
        correlation = np.corrcoef(arr1.flatten(), arr2.flatten())[0, 1]
        
        return max(0, min(1, correlation))  # Ensure result is between 0 and 1
    except Exception as e:
        logging.error(f"Error comparing images: {e}")
        return 0.0

def extract_text_from_image(
    image_path: str,
    lang: str = 'eng'
) -> str:
    """
    Extract text from an image file using OCR
    
    Args:
        image_path: Path to image file
        lang: OCR language
        
    Returns:
        Extracted text
    """
    try:
        return pytesseract.image_to_string(Image.open(image_path), lang=lang)
    except Exception as e:
        logging.error(f"Error extracting text from image: {e}")
        return ""

def get_colors_at_point(
    x: int,
    y: int
) -> Tuple[int, int, int]:
    """
    Get RGB color values at a specific screen coordinate
    
    Args:
        x, y: Screen coordinates
        
    Returns:
        (R, G, B) color tuple
    """
    try:
        screenshot = ImageGrab.grab(bbox=(x, y, x+1, y+1))
        return screenshot.getpixel((0, 0))
    except Exception as e:
        logging.error(f"Error getting color at point: {e}")
        return (0, 0, 0)

def save_debug_info(
    data: Dict[str, Any],
    filename: Optional[str] = None
) -> None:
    """
    Save debug information to a file
    
    Args:
        data: Debug data to save
        filename: Optional filename (default: timestamp-based)
    """
    import json
    
    # Create debug directory
    debug_dir = "debug"
    os.makedirs(debug_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = int(time.time())
        filename = f"debug_{timestamp}.json"
    
    # Ensure filename has .json extension
    if not filename.lower().endswith('.json'):
        filename += '.json'
    
    # Full path to save
    filepath = os.path.join(debug_dir, filename)
    
    # Save data as JSON
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Saved debug info to {filepath}")
    except Exception as e:
        logging.error(f"Error saving debug info: {e}")

# Example usage
if __name__ == "__main__":
    # Take a screenshot of the entire screen
    screenshot_path = save_screenshot()
    
    # Extract text from the screenshot
    text = extract_text_from_image(screenshot_path)
    print(f"Extracted text:\n{text}")
    
    # Save debug info
    save_debug_info({
        "screenshot_path": screenshot_path,
        "extracted_text": text,
        "screen_size": pyautogui.size()
    })