# Image Compression for Screenshots

## Overview

This update integrates image compression functionality for all screenshots taken by the vision detection system. This helps reduce memory usage and improve performance when processing images with vision models.

## Changes Made

1. **Added `image_processing_utils.py` to the project:**
   - Created a new file in `python_cli/src/image_processing_utils.py` with compression utilities
   - The code is based on the existing `examples/image_processing_utils.py`
   - Main function is `compress_image()` which reduces image size and quality to stay below a specified size threshold

2. **Modified `vision_detection.py`:**
   - Added imports for the compression utilities
   - Updated the `_save_temp_screenshot()` method to compress screenshots before saving
   - Added error handling for cases where compression might fail

3. **Modified `site_vision.py`:**
   - Added imports for the compression utilities
   - Updated all calls to `save_screenshot()` to use compression
   - Set default compression threshold to 500KB

4. **Modified `utils.py`:**
   - Added imports for the compression utilities
   - Enhanced the `save_screenshot()` function to support compression
   - Added parameters for controlling compression (enabled by default)

5. **Import handling:**
   - Added fallback logic to try importing from local directory first, then from examples
   - Added proper error handling if the compression utilities can't be found

## How It Works

1. When a screenshot is captured using `ImageGrab.grab()`, it is initially saved as a temporary file
2. The image is then compressed using `compress_image()` to reduce its size while maintaining quality
3. The compressed image is used for all further processing, such as sending to vision models
4. Debug screenshots saved to disk are also compressed automatically

## Benefits

- Reduced memory usage when processing multiple screenshots
- Faster upload times when sending images to vision models
- Smaller disk space usage for debug screenshots
- Better performance on machines with limited resources

## Usage

The compression is enabled by default, but can be controlled:

```python
# To disable compression for a specific screenshot:
save_screenshot("example.png", directory="debug", compress=False)

# To adjust the maximum size:
save_screenshot("example.png", directory="debug", compress=True, max_size_kb=1000)
```

The compression system attempts to maintain image quality while reducing size by:
1. First reducing JPEG quality
2. If necessary, gradually reducing image dimensions
3. Using up to 5 attempts to get below the size threshold

## Fallback Behavior

If the compression utilities can't be imported or if compression fails for any reason, the system will gracefully fall back to using the original uncompressed images, ensuring the core functionality continues to work.