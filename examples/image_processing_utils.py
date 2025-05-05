### `src/mcp_doc_retriever/context7/image_processing_utils.py`

import base64
import hashlib
from typing import Any, Dict
import mimetypes
from pathlib import Path
from PIL import Image
import os
from loguru import logger
import requests

def download_and_cache_image(url: str, image_directory: str) -> str:
    """
    Downloads an image from the given URL and stores it in the image directory.

    Args:
        url (str): The URL of the image.
        image_directory (str): Directory to store cached images.

    Returns:
        str: Path to the cached image.
    """
    # Ensure image directory exists
    Path(image_directory).mkdir(parents=True, exist_ok=True)
    
    # Generate a unique filename based on the URL's hash
    url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
    cached_image_path = Path(image_directory) / f"{url_hash}.jpg"
    
    # If the file is already cached, return its path
    if cached_image_path.exists():
        return str(cached_image_path)

    # Download the image
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes
        with open(cached_image_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Downloaded image from {url} to {cached_image_path}")
        return str(cached_image_path)
    except requests.RequestException as e:
        logger.error(f"Failed to download image from {url}: {e}")
        raise ValueError(f"Failed to download image: {url}")


def process_image_input(image_input: str, image_directory: str, max_size_kb: int = 500) -> Dict[str, Any]:
    """
    Processes an image input and returns a structured content dictionary.

    Args:
        image_input (str): The image input, which can be an external URL, a Base64 string, or a local file path.
        image_directory (str): Directory to store compressed images.
        max_size_kb (int): Maximum size for compressed images in KB.

    Returns:
        Dict[str, Any]: A dictionary representing the processed image in the required format.
    """
    if image_input.startswith("http"):  # External URL
        return {"type": "image_url", "image_url": {"url": image_input}}
    elif image_input.startswith("data:image"):  # Base64 string
        compressed_base64_image = decode_base64_image(image_input, image_directory, max_size_kb)
        return {"type": "image_url", "image_url": {"url": compressed_base64_image}}
    else:  # Assume local file path
        compressed_image_path = compress_image(image_input, image_directory, max_size_kb)
        base64_image = convert_image_to_base64(compressed_image_path)
        return {"type": "image_url", "image_url": {"url": base64_image}}


def compress_image(image_path: str, image_directory: str, max_size_kb: int, max_attempts: int = 5, resize_step: int = 10) -> str:
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
        img_format = img.format or "JPEG"  # Default to JPEG if format is unknown
        quality = 90  # Initial compression quality
        width, height = img.size  # Original dimensions

        for attempt in range(max_attempts):
            # Save the image with current quality and dimensions
            img.save(compressed_file_path, format=img_format, quality=quality, optimize=True)
            compressed_size_kb = os.path.getsize(compressed_file_path) / 1024

            if compressed_size_kb <= max_size_kb:
                return compressed_file_path

            # If compression alone doesn't work, reduce dimensions
            if attempt < max_attempts - 1:  # Avoid resizing on the last attempt
                width = int(width * (1 - resize_step / 100))
                height = int(height * (1 - resize_step / 100))
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                logger.info(f"Resizing image to {width}x{height} for attempt {attempt + 1}.")

            quality = max(10, quality - 10)  # Reduce quality for further compression

        logger.warning(f"Could not compress {image_path} under {max_size_kb}KB after {max_attempts} attempts.")
        return image_path
    except Exception as e:
        logger.exception(f"Error compressing image {image_path}: {e}")
        return image_path


def decode_base64_image(base64_image: str, image_directory: str, max_size_kb: int) -> str:
    """
    Decode a Base64-encoded image, check its size, and compress it if necessary.

    Args:
        base64_image (str): The Base64-encoded image string.
        image_directory (str): Directory to store the temporary decoded image.
        max_size_kb (int): Maximum size allowed for the compressed image in KB.

    Returns:
        str: A Base64-encoded string of the compressed image.

    Raises:
        ValueError: If the input Base64 string is invalid or the compression fails.
    """
    try:
        # Extract Base64 data
        base64_data = base64_image.split(",")[1] if "," in base64_image else base64_image
        image_data = base64.b64decode(base64_data)

        # Save the decoded image as a temporary file
        temp_image_path = os.path.join(image_directory, "temp_decoded_image.jpg")
        with open(temp_image_path, "wb") as f:
            f.write(image_data)

        # Check size of the original Base64 image
        original_size_kb = os.path.getsize(temp_image_path) / 1024
        if original_size_kb <= max_size_kb:
            logger.info(f"Base64 image is already within the size threshold ({original_size_kb}KB).")
            return base64_image

        # Compress the image if it exceeds the size threshold
        compressed_image_path = compress_image(temp_image_path, image_directory, max_size_kb)
        if not compressed_image_path:
            raise ValueError("Failed to compress Base64 image to an appropriate size.")

        # Re-encode the compressed image to Base64
        with open(compressed_image_path, "rb") as f:
            compressed_base64 = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode('utf-8')}"

        logger.info(f"Compressed Base64 image to meet the size threshold ({max_size_kb}KB).")
        return compressed_base64
    except Exception as e:
        logger.error(f"Error decoding and compressing Base64 image: {e}")
        raise ValueError("Invalid Base64 image or compression failure.")


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
            logger.error(f"Image file does not exist: {image_path}")
            return ""
        if not path.is_file():
            logger.error(f"Provided path is not a file: {image_path}")
            return ""

        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(path)
        if not mime_type or not mime_type.startswith("image/"):
            logger.error(f"File is not a recognized image type: {image_path}")
            return ""

        # Read and encode the image file
        with path.open("rb") as image_file:
            base64_encoded = base64.b64encode(image_file.read()).decode("utf-8")
            logger.info(f"Successfully converted {image_path} to Base64.")
            return f"data:{mime_type};base64,{base64_encoded}"
    
    except FileNotFoundError:
        logger.exception(f"File not found: {image_path}")
    except PermissionError:
        logger.exception(f"Permission denied: {image_path}")
    except Exception as e:
        logger.exception(f"Failed to convert image to Base64: {e}")

    return ""


