"""
QWen-VL model processor for UI element detection and interaction.

This module provides a sophisticated implementation for using the QWen-VL model
to detect UI elements on screen, recognize CAPTCHAs, and extract text from
screenshots. It handles device management (CPU/CUDA), model caching through a
singleton pattern, and provides robust error handling.

The QwenVLProcessor class implements a singleton pattern to ensure efficient memory
usage when processing multiple screenshots by loading the model only once.

Third-party package documentation:
- transformers: https://huggingface.co/docs/transformers/
- torch: https://pytorch.org/docs/stable/
- Qwen2.5-VL: https://huggingface.co/Qwen/Qwen2.5-VL-7B

Example usage:
    >>> from src.qwen_processor import QwenVLProcessor
    >>> from PIL import ImageGrab
    >>> processor = QwenVLProcessor()  # Loads model only once
    >>> screenshot = ImageGrab.grab()
    >>> elements = processor.detect_ui_elements(screenshot, "qwen")
    >>> print(f"Found input field at: {elements.get('input_field')}")
"""

import os
import sys
import json
import time
import tempfile
import logging
from typing import Optional, Dict, List, Any, Union, Tuple
from pathlib import Path
from PIL import ImageGrab, Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Handle required dependencies
try:
    import torch
except ImportError:
    logging.warning("torch package not found. Install with: pip install torch")
    torch = None

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
except ImportError:
    logging.warning("transformers package not found. Install with: pip install transformers")
    AutoTokenizer = None
    AutoModelForCausalLM = None

# Default configuration
DEFAULT_MODEL_NAME = "Qwen/Qwen2.5-VL-3B-Instruct"  # Using 3B parameter model which should be available
DEFAULT_MAX_NEW_TOKENS = 1024

# Prompts for different detection tasks
UI_DETECTION_PROMPT = """
I need to find UI elements in this screenshot of an AI chat interface.

For each element below, tell me if you can see it in the image and give me both:
1. The X,Y coordinates of its center (0,0 is top-left)
2. The bounding box coordinates [x1, y1, x2, y2] where x1,y1 is top-left and x2,y2 is bottom-right

Elements to identify:
1. The chat input field or text area (where users type messages)
2. The send button (might be an arrow, paper plane icon, or similar)
3. The most recent AI response text area

Return your answer as a JSON object with these keys:
- "input_field": {"center": [x, y], "box": [x1, y1, x2, y2]} or null if not found
- "send_button": {"center": [x, y], "box": [x1, y1, x2, y2]} or null if not found
- "response_area": {"center": [x, y], "box": [x1, y1, x2, y2]} or null if not found

Include a brief description of each element's appearance.
"""

CAPTCHA_DETECTION_PROMPT = """
Look at this screenshot and determine if there is a CAPTCHA or human verification challenge visible.

Examples of what to look for:
- Any text mentioning "CAPTCHA", "verification", "prove you're human", etc.
- Image-based CAPTCHA puzzles
- Checkbox challenges like "I'm not a robot"
- Slider puzzles or other interactive verification mechanisms

Is there a CAPTCHA or human verification challenge visible? 
Return your answer as a JSON object with:
- "captcha_detected": true or false
- "description": brief description of what you found (if anything)
"""

EXTRACT_TEXT_PROMPT = """
Extract the complete text of the AI's response from this screenshot.

Return your answer as a JSON object with:
- "response_text": the complete text of the AI's response
- "confidence": your confidence level (0-1) in the extraction accuracy
"""

class QwenVLProcessor:
    """Singleton processor for QWen-VL model with specialized UI detection."""
    
    _instance = None
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        """
        Initialize the QWen-VL processor
        
        Args:
            model_name: Name of the model to load (default: Qwen/Qwen2.5-VL-7B)
        """
        self.model_name = model_name
        self.device = "cuda" if torch and torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        self._model_loaded = False
        
        # Log initialization but don't load model yet (lazy loading)
        logging.info(f"Initialized QwenVLProcessor with {model_name} (device: {self.device})")

    def __new__(cls, *args, **kwargs):
        """Ensure singleton pattern - only one instance is ever created."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self) -> bool:
        """
        Load the QWen-VL model and tokenizer if not already loaded
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        if self._model_loaded:
            return True
            
        try:
            if AutoTokenizer is None or AutoModelForCausalLM is None:
                raise ImportError("transformers package not available")
                
            logging.info(f"Loading {self.model_name} model...")
            
            if self.device == "cpu":
                logging.warning("Using CPU for inference - this may be slow")
                
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, 
                trust_remote_code=True
            )
            
            # Load model with appropriate configuration
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map=self.device,
                trust_remote_code=True
            )
            
            self._model_loaded = True
            logging.info("Model loaded successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to load QWen-VL model: {e}")
            self.model = None
            self.tokenizer = None
            self._model_loaded = False
            return False

    def unload_model(self) -> None:
        """Unload the model to free up memory."""
        if self.model is not None:
            del self.model
            del self.tokenizer
            self.model = None
            self.tokenizer = None
            self._model_loaded = False
            
            # Clean up CUDA memory if available
            if torch and torch.cuda.is_available():
                torch.cuda.empty_cache()
                
            logging.info("Model unloaded")

    def _process_with_model(
        self, 
        image: Image.Image, 
        prompt: str,
        max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS
    ) -> str:
        """
        Process an image with the model and return the response
        
        Args:
            image: PIL Image to process
            prompt: Text prompt for the model
            max_new_tokens: Maximum number of tokens to generate
            
        Returns:
            Model response as string
            
        Raises:
            RuntimeError: If model loading fails or processing fails
        """
        # Ensure model is loaded
        if not self._model_loaded and not self.load_model():
            raise RuntimeError("Failed to load QWen-VL model")
            
        try:
            # Prepare prompt with image
            messages = [
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image", "image": image}
                ]}
            ]
            
            # Generate model inputs
            model_inputs = self.tokenizer.apply_chat_template(
                messages, 
                return_tensors="pt"
            ).to(self.model.device)
            
            # Generate response
            with torch.no_grad():
                generated_ids = self.model.generate(
                    model_inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=False
                )
                
            # Decode and extract response
            response = self.tokenizer.decode(
                generated_ids[0][model_inputs.shape[1]:], 
                skip_special_tokens=True
            )
            
            return response
            
        except Exception as e:
            logging.error(f"Error processing image with model: {e}")
            raise RuntimeError(f"Image processing failed: {e}")

    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        Extract JSON object from model response
        
        Args:
            response: Model response text
            
        Returns:
            Extracted JSON as dictionary, or empty dict if extraction fails
        """
        try:
            # Look for JSON block in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                logging.warning("No JSON found in response")
                return {}
                
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON from response: {e}")
            return {}

    def detect_ui_elements(
        self, 
        image: Optional[Image.Image] = None,
        site_name: str = "chat"
    ) -> Dict[str, Dict[str, Optional[Union[Tuple[int, int], List[int]]]]]:
        """
        Detect UI elements in a screenshot
        
        Args:
            image: Screenshot image (if None, takes a new screenshot)
            site_name: Name of the site for customized prompts
            
        Returns:
            Dictionary with coordinates and bounding boxes of detected UI elements
        """
        # Take screenshot if not provided
        if image is None:
            image = ImageGrab.grab()
            
        # Create site-specific prompt
        if site_name.lower() == "qwen":
            site_desc = "the Qwen.ai chat interface"
        elif site_name.lower() in ("perplexity", "pplx"):
            site_desc = "the Perplexity.ai chat interface"
        else:
            site_desc = f"a {site_name} chat interface"
            
        prompt = UI_DETECTION_PROMPT.replace("an AI chat interface", site_desc)
        
        try:
            # Process with model
            response = self._process_with_model(image, prompt)
            
            # Extract JSON
            results = self._extract_json_from_response(response)
            
            # Convert to expected format
            elements = {}
            
            # Process input field
            elements["input_field"] = {"center": None, "box": None}
            if "input_field" in results and isinstance(results["input_field"], dict):
                if "center" in results["input_field"] and isinstance(results["input_field"]["center"], list) and len(results["input_field"]["center"]) == 2:
                    elements["input_field"]["center"] = tuple(results["input_field"]["center"])
                if "box" in results["input_field"] and isinstance(results["input_field"]["box"], list) and len(results["input_field"]["box"]) == 4:
                    elements["input_field"]["box"] = results["input_field"]["box"]
                    
            # Process send button
            elements["send_button"] = {"center": None, "box": None}
            if "send_button" in results and isinstance(results["send_button"], dict):
                if "center" in results["send_button"] and isinstance(results["send_button"]["center"], list) and len(results["send_button"]["center"]) == 2:
                    elements["send_button"]["center"] = tuple(results["send_button"]["center"])
                if "box" in results["send_button"] and isinstance(results["send_button"]["box"], list) and len(results["send_button"]["box"]) == 4:
                    elements["send_button"]["box"] = results["send_button"]["box"]
                
            # Process response area
            elements["response_area"] = {"center": None, "box": None}
            if "response_area" in results and isinstance(results["response_area"], dict):
                if "center" in results["response_area"] and isinstance(results["response_area"]["center"], list) and len(results["response_area"]["center"]) == 2:
                    elements["response_area"]["center"] = tuple(results["response_area"]["center"])
                if "box" in results["response_area"] and isinstance(results["response_area"]["box"], list) and len(results["response_area"]["box"]) == 4:
                    elements["response_area"]["box"] = results["response_area"]["box"]
                
            logging.info(f"Detected UI elements: {elements}")
            return elements
            
        except Exception as e:
            logging.error(f"UI element detection failed: {e}")
            return {
                "input_field": {"center": None, "box": None}, 
                "send_button": {"center": None, "box": None}, 
                "response_area": {"center": None, "box": None}
            }

    def detect_captcha(
        self, 
        image: Optional[Image.Image] = None
    ) -> Tuple[bool, str]:
        """
        Detect if a CAPTCHA is present in a screenshot
        
        Args:
            image: Screenshot image (if None, takes a new screenshot)
            
        Returns:
            Tuple of (captcha_detected, description)
        """
        # Take screenshot if not provided
        if image is None:
            image = ImageGrab.grab()
            
        try:
            # Process with model
            response = self._process_with_model(image, CAPTCHA_DETECTION_PROMPT)
            
            # Extract JSON
            results = self._extract_json_from_response(response)
            
            # Get results
            captcha_detected = results.get("captcha_detected", False)
            description = results.get("description", "")
            
            if captcha_detected:
                logging.warning(f"CAPTCHA detected: {description}")
            else:
                logging.info("No CAPTCHA detected")
                
            return captcha_detected, description
            
        except Exception as e:
            logging.error(f"CAPTCHA detection failed: {e}")
            return False, f"Detection error: {e}"

    def extract_response_text(
        self, 
        image: Optional[Image.Image] = None
    ) -> str:
        """
        Extract AI response text from a screenshot
        
        Args:
            image: Screenshot image (if None, takes a new screenshot)
            
        Returns:
            Extracted response text
        """
        # Take screenshot if not provided
        if image is None:
            image = ImageGrab.grab()
            
        try:
            # Process with model
            response = self._process_with_model(
                image, 
                EXTRACT_TEXT_PROMPT,
                max_new_tokens=2000  # Longer for text extraction
            )
            
            # Extract JSON
            results = self._extract_json_from_response(response)
            
            # Get extracted text
            text = results.get("response_text", "")
            confidence = results.get("confidence", 0.0)
            
            if text:
                logging.info(f"Successfully extracted response text ({len(text)} chars, confidence: {confidence:.2f})")
                return text
            else:
                # If JSON extraction failed, return the full response
                logging.warning("Failed to extract structured response text, using full response")
                return response.strip()
                
        except Exception as e:
            logging.error(f"Response text extraction failed: {e}")
            return f"Extraction error: {e}"

    def save_debug_screenshot(
        self, 
        image: Optional[Image.Image] = None,
        prefix: str = "debug"
    ) -> str:
        """
        Save a screenshot for debugging purposes
        
        Args:
            image: Screenshot image (if None, takes a new screenshot)
            prefix: Prefix for the filename
            
        Returns:
            Path to saved screenshot
        """
        # Take screenshot if not provided
        if image is None:
            image = ImageGrab.grab()
            
        # Create debug directory if it doesn't exist
        debug_dir = Path("debug")
        debug_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{prefix}_{timestamp}.png"
        filepath = debug_dir / filename
        
        # Save image
        image.save(filepath)
        logging.info(f"Saved debug screenshot to {filepath}")
        
        return str(filepath)

# Example usage
if __name__ == "__main__":
    # Set up logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("QWEN-VL PROCESSOR TESTING")
    print("=========================")
    
    # Test the processor
    processor = QwenVLProcessor()
    
    # Wait for user to position window
    input("Position your browser window with a chat interface and press Enter...")
    
    # Take screenshot
    screenshot = ImageGrab.grab()
    processor.save_debug_screenshot(screenshot, "test_screenshot")
    
    # Load model if not already loaded
    if not processor._model_loaded:
        processor.load_model()
    
    # Detect UI elements
    print("\nDetecting UI elements...")
    elements = processor.detect_ui_elements(screenshot, "qwen")
    
    print("Results:")
    for element, coords in elements.items():
        print(f"- {element}: {coords}")
    
    # Check for CAPTCHA
    print("\nChecking for CAPTCHA...")
    captcha_present, captcha_desc = processor.detect_captcha(screenshot)
    print(f"CAPTCHA detected: {captcha_present}")
    if captcha_present:
        print(f"Description: {captcha_desc}")
    
    # Extract response text if there's content
    print("\nExtracting any response text...")
    text = processor.extract_response_text(screenshot)
    print(f"Extracted text length: {len(text)}")
    print(f"Preview: {text[:200]}..." if len(text) > 200 else text)
    
    # Unload model to free memory
    processor.unload_model()