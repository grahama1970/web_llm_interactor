#!/usr/bin/env python3
"""
Image processing utilities for AI chat automation
Handles compression and optimization of images before being processed by vision models
"""

import base64
import hashlib
from typing import Any, Dict
import mimetypes
from pathlib import Path
import os
import logging
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("image_processing.log"),
        logging.StreamHandler()
    ]
)

def compress_image(image_path: str, image_directory: str, max_size_kb: int = 500, max_attempts: int = 5, resize_step: int = 10) -> str:
    """
    Compress and resize an image file to be under the size threshold.

    Args:
        image_path (str): Path to the original image file.
        image_directory (str): Directory to store compressed images.
        max_size_kb (int): Maximum size allowed for the compressed image in KB.
        max_attempts (int): Maximum number of compression attempts.
        resize_step (int): Percentage step to reduce image dimensions during resizing.

    Returns:
        str: Path to the compressed image file, or the original image if compression failed.
    """
    os.makedirs(image_directory, exist_ok=True)  # Ensure directory exists
    original_file_name = os.path.basename(image_path)
    compressed_file_path = os.path.join(image_directory, f"{os.path.splitext(original_file_name)[0]}_compressed.jpg")

    # If compressed file already exists, return its path
    if os.path.exists(compressed_file_path):
        return compressed_file_path

    try:
        img = Image.open(image_path)
        
        # Convert RGBA to RGB if needed
        if img.mode == 'RGBA':
            img = img.convert('RGB')
            
        img_format = img.format or "JPEG"  # Default to JPEG if format is unknown
        quality = 90  # Initial compression quality
        width, height = img.size  # Original dimensions

        for attempt in range(max_attempts):
            # Save the image with current quality and dimensions
            img.save(compressed_file_path, format=img_format, quality=quality, optimize=True)
            compressed_size_kb = os.path.getsize(compressed_file_path) / 1024

            if compressed_size_kb <= max_size_kb:
                logging.info(f"Successfully compressed image to {compressed_size_kb:.2f}KB ({width}x{height}, quality={quality})")
                return compressed_file_path

            # If compression alone doesn't work, reduce dimensions
            if attempt < max_attempts - 1:  # Avoid resizing on the last attempt
                width = int(width * (1 - resize_step / 100))
                height = int(height * (1 - resize_step / 100))
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                logging.info(f"Resizing image to {width}x{height} for attempt {attempt + 1}.")

            quality = max(10, quality - 10)  # Reduce quality for further compression

        logging.warning(f"Could not compress {image_path} under {max_size_kb}KB after {max_attempts} attempts.")
        return image_path
    except Exception as e:
        logging.exception(f"Error compressing image {image_path}: {e}")
        return image_path

def compress_image_object(img: Image.Image, image_directory: str, filename: str = "temp", max_size_kb: int = 500) -> str:
    """
    Compress an Image object directly and save to a file.

    Args:
        img (Image.Image): PIL Image object to compress
        image_directory (str): Directory to store compressed images
        filename (str): Base filename to use for the compressed image
        max_size_kb (int): Maximum size allowed for the compressed image in KB

    Returns:
        str: Path to the compressed image file
    """
    os.makedirs(image_directory, exist_ok=True)  # Ensure directory exists
    temp_path = os.path.join(image_directory, f"{filename}_original.jpg")
    compressed_path = os.path.join(image_directory, f"{filename}_compressed.jpg")

    try:
        # Convert RGBA to RGB if needed
        if img.mode == 'RGBA':
            img = img.convert('RGB')
            
        # Save original image to a temporary file
        img.save(temp_path, format="JPEG")
        
        # Compress the saved image
        result_path = compress_image(temp_path, image_directory, max_size_kb)
        
        # Clean up the temporary file if it's not the same as the result
        if temp_path != result_path and os.path.exists(temp_path):
            os.remove(temp_path)
            
        return result_path
    except Exception as e:
        logging.exception(f"Error compressing image object: {e}")
        
        # If compression failed but we saved the original, return that
        if os.path.exists(temp_path):
            return temp_path
            
        # If everything failed, return None
        return None

def convert_image_to_base64(image_path: str) -> str:
    """
    Converts an image file to a Base64-encoded string.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Base64-encoded string of the image, or an empty string on failure.
    """
    try:
        # Validate the image path
        path = Path(image_path)
        if not path.exists():
            logging.error(f"Image file does not exist: {image_path}")
            return ""
        if not path.is_file():
            logging.error(f"Provided path is not a file: {image_path}")
            return ""

        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(path)
        if not mime_type or not mime_type.startswith("image/"):
            logging.error(f"File is not a recognized image type: {image_path}")
            return ""

        # Read and encode the image file
        with path.open("rb") as image_file:
            base64_encoded = base64.b64encode(image_file.read()).decode("utf-8")
            logging.info(f"Successfully converted {image_path} to Base64.")
            return f"data:{mime_type};base64,{base64_encoded}"
    
    except FileNotFoundError:
        logging.exception(f"File not found: {image_path}")
    except PermissionError:
        logging.exception(f"Permission denied: {image_path}")
    except Exception as e:
        logging.exception(f"Failed to convert image to Base64: {e}")

    return ""