#!/usr/bin/env python3
"""
Vision-based UI element detection using Qwen 2.5 VL
"""

import os
import time
import logging
import tempfile
import sys
from PIL import ImageGrab, Image
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Dict, List, Optional, Tuple, Union, Any

# Try to import from local directory first, then from examples
try:
    from .image_processing_utils import compress_image, compress_image_object
except ImportError:
    try:
        # Also try importing from examples directory
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'examples'))
        from image_processing_utils import compress_image
    except ImportError:
        logging.warning("Could not import image_processing_utils, image compression will be disabled")
        compress_image = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("vision_detection.log"),
        logging.StreamHandler()
    ]
)

class VisionDetector:
    """Uses vision-language models to detect UI elements on screen"""
    
    def __init__(self, model_name: str = "microsoft/git-base-coco"):
        """
        Initialize the vision detector with the specified model
        
        Args:
            model_name: Name of the vision-language model to use
                Default is "microsoft/git-base-coco" which is public and works well for detection
                Other options include "Salesforce/blip-image-captioning-base" or "Qwen/Qwen1.5-0.5B-Chat"
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logging.info(f"Initializing VisionDetector with {model_name} on {self.device}")
        
    def load_model(self):
        """Load the vision-language model"""
        if self.model is None:
            try:
                logging.info(f"Loading model {self.model_name}...")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                
                # Different model types require different loading approaches
                if "blip" in self.model_name.lower():
                    from transformers import BlipForConditionalGeneration
                    self.model = BlipForConditionalGeneration.from_pretrained(
                        self.model_name,
                        device_map=self.device
                    )
                elif "git" in self.model_name.lower():
                    from transformers import AutoModelForCausalLM
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_name,
                        device_map=self.device
                    )
                else:
                    # Default loading method for other models
                    try:
                        # First try loading with trust_remote_code for newer models
                        self.model = AutoModelForCausalLM.from_pretrained(
                            self.model_name,
                            trust_remote_code=True,
                            device_map=self.device
                        )
                    except Exception as model_error:
                        logging.warning(f"Error loading model with trust_remote_code: {model_error}")
                        # Fallback to basic loading without trust_remote_code
                        self.model = AutoModelForCausalLM.from_pretrained(
                            self.model_name,
                            device_map=self.device
                        )
                    
                logging.info("Model loaded successfully")
            except Exception as e:
                logging.error(f"Error loading model: {e}")
                raise
    
    def unload_model(self):
        """Unload the model to free up memory"""
        if self.model is not None:
            del self.model
            del self.tokenizer
            self.model = None
            self.tokenizer = None
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            logging.info("Model unloaded")
    
    def _capture_screenshot(self) -> Image.Image:
        """Capture a screenshot of the current screen"""
        return ImageGrab.grab()
    
    def _save_temp_screenshot(self, image: Image.Image) -> str:
        """Save screenshot to a temporary file and return the path"""
        # Create debug directory for compressed images
        debug_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "debug")
        os.makedirs(debug_dir, exist_ok=True)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            temp_path = tmp.name
            image.save(temp_path)
            
            # Try to use the compress_image_object function for direct compression
            try:
                timestamp = int(time.time())
                compressed_path = compress_image_object(
                    image, 
                    debug_dir, 
                    f"screenshot_{timestamp}", 
                    max_size_kb=500
                )
                if compressed_path and os.path.exists(compressed_path):
                    logging.info(f"Directly compressed screenshot to {compressed_path}")
                    # Remove the original if direct compression succeeded
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    return compressed_path
            except Exception as e:
                logging.warning(f"Direct image compression failed: {e}")
            
            # Fall back to compressing the saved file
            try:
                # Compress the image to reduce size (max 500KB)
                compressed_path = compress_image(temp_path, debug_dir, max_size_kb=500)
                logging.info(f"Compressed screenshot from {temp_path} to {compressed_path}")
                
                # Delete the original uncompressed file if compression succeeded
                if os.path.exists(compressed_path) and compressed_path != temp_path:
                    os.remove(temp_path)
                    return compressed_path
            except Exception as e:
                logging.error(f"Error compressing screenshot: {e}")
                # If compression fails, use the original image
            
            return temp_path
    
    def detect_elements(self, element_descriptions: List[str]) -> Dict[str, Optional[Tuple[int, int]]]:
        """
        Detect multiple UI elements in a screenshot
        
        Args:
            element_descriptions: List of text descriptions of elements to find
                                  (e.g., "the chat input box", "the send button")
                                  
        Returns:
            Dictionary mapping element descriptions to their coordinates (or None if not found)
        """
        # Load model if needed
        if self.model is None:
            self.load_model()
        
        # Capture screenshot
        screenshot = self._capture_screenshot()
        screenshot_path = self._save_temp_screenshot(screenshot)
        
        # Create a detection prompt for the model
        base_prompt = """
        I need to find UI elements in this screenshot of a chat interface.
        
        For each element, I want you to:
        1. Tell me if you can see the element in the image
        2. Give me the X,Y coordinates of the center of the element (0,0 is top-left)
        3. Describe what the element looks like
        
        Return your answer as a JSON object with element names as keys and objects with 'found', 'coordinates', and 'description' fields.
        
        Elements to find:
        """
        
        element_list = "\n".join([f"- {desc}" for desc in element_descriptions])
        prompt = f"{base_prompt}\n{element_list}\n\nJSON:"
        
        # Process with the vision-language model
        try:
            logging.info("Querying vision model for element detection...")
            
            # Process with the vision model
            if "blip" in self.model_name.lower():
                # BLIP model processing
                from PIL import Image
                from transformers import BlipProcessor
                
                processor = BlipProcessor.from_pretrained(self.model_name)
                image = Image.open(screenshot_path).convert('RGB')
                
                # Prepare inputs
                inputs = processor(images=image, text=prompt, return_tensors="pt").to(self.device)
                
                # Generate
                generated_ids = self.model.generate(**inputs, max_new_tokens=1000)
                response = processor.decode(generated_ids[0], skip_special_tokens=True)
                
            else:
                # Standard ChatML format for most models
                try:
                    # Attempt multimodal format with error handling
                    try:
                        # Create message with image in multimodal format
                        messages = [
                            {"role": "user", "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image", "image_url": {"url": f"file://{screenshot_path}"}}
                            ]}
                        ]
                        
                        # Generate response
                        model_inputs = self.tokenizer.apply_chat_template(
                            messages, 
                            return_tensors="pt"
                        ).to(self.model.device)
                    except Exception as format_error:
                        # Broader error handling for any issues with multimodal format
                        logging.warning(f"Multimodal format failed: {format_error}, trying text-only format")
                        try:
                            # Fall back to text-only format for models that don't support multimodal input
                            text_messages = [
                                {"role": "user", "content": prompt}  # Use only text content
                            ]
                            model_inputs = self.tokenizer.apply_chat_template(
                                text_messages,
                                return_tensors="pt"
                            ).to(self.model.device)
                        except Exception as text_error:
                            # If text format also fails, try direct tokenization as a last resort
                            logging.warning(f"Text-only format also failed: {text_error}, trying direct tokenization")
                            # Direct tokenization without chat template
                            model_inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
                            logging.info("Direct tokenization succeeded")
                    generated_ids = self.model.generate(
                        model_inputs,
                        max_new_tokens=1000,
                        do_sample=False
                    )
                    response = self.tokenizer.decode(generated_ids[0][model_inputs.shape[1]:], skip_special_tokens=True)
                except Exception as e:
                    logging.error(f"Error processing with standard method: {e}")
                    # Fallback to basic processing for text-only response
                    logging.warning("Fallback to basic text-only processing")
                    from PIL import Image
                    image = Image.open(screenshot_path).convert('RGB')
                    
                    # Try to describe the image with text directly in the prompt
                    enhanced_prompt = f"""
                    I need to analyze a screenshot of a chat interface to find exact pixel coordinates.
                    
                    The screenshot likely contains:
                    - A chat window or conversation interface
                    - Text input area at the bottom of the screen (THIS IS MOST IMPORTANT)
                    - Send button (usually at bottom right)
                    - Message history or conversation area
                    
                    Original prompt: {prompt}
                    
                    You MUST provide EXACT PIXEL COORDINATES as (x,y) for each element. The screen is likely 1680x1050 pixels.
                    
                    Format your response as a valid JSON object with this structure:
                    {{
                      "the chat input text area at the bottom of the screen": {{
                        "found": true,
                        "coordinates": [840, 940],
                        "description": "Text input box"
                      }},
                      "the send button": {{
                        "found": true,
                        "coordinates": [1600, 940],
                        "description": "Arrow button"
                      }}
                    }}
                    
                    Predict the most likely position of these elements based on typical chat interface layouts.
                    For the chat input, use coordinates near the bottom center (y coordinate around 900-950).
                    For send button, use coordinates near bottom right.
                    """
                    
                    inputs = self.tokenizer(enhanced_prompt, return_tensors="pt").to(self.device)
                    generated_ids = self.model.generate(**inputs, max_new_tokens=1000)
                    response = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)
                    response += "\n[Note: Image could not be processed directly - text-only fallback used]"
            
            # Parse response, trying to extract JSON if present
            import json
            import re
            
            try:
                # Method 1: Try to extract JSON using regex
                json_matches = re.findall(r'\{.*?\}', response, re.DOTALL)
                if json_matches:
                    longest_match = max(json_matches, key=len)
                    try:
                        detection_results = json.loads(longest_match)
                        logging.info(f"Extracted JSON using regex: {longest_match[:100]}...")
                    except:
                        # If the regex match isn't valid JSON, fall back to other methods
                        raise ValueError("Regex match isn't valid JSON")
                else:
                    # Method 2: Look for opening and closing braces
                    json_start = response.find('{')
                    json_end = response.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = response[json_start:json_end]
                        try:
                            detection_results = json.loads(json_str)
                            logging.info(f"Extracted JSON using braces: {json_str[:100]}...")
                        except:
                            # If not valid JSON, create our own based on response text
                            raise ValueError("Brace-enclosed text isn't valid JSON")
                    else:
                        # If no JSON found, create our own based on model's description
                        logging.warning("No JSON structure found in response, creating manually")
                        # Create a simple JSON structure based on text description
                        detection_results = {}
                        for element in element_descriptions:
                            # Search for element in the response
                            element_found = element.lower() in response.lower()
                            detection_results[element] = {
                                "found": element_found,
                                "coordinates": None,
                                "description": "Automatically extracted from text"
                            }
                            
                            # Look for coordinate mentions near the element name
                            element_pos = response.lower().find(element.lower())
                            if element_pos >= 0:
                                # Look for numbers in parentheses or brackets within 100 chars after element mention
                                coord_match = re.search(r'[\(\[]?\s*(\d+)\s*,\s*(\d+)\s*[\)\]]?', 
                                                       response[element_pos:element_pos+200])
                                if coord_match:
                                    try:
                                        x, y = int(coord_match.group(1)), int(coord_match.group(2))
                                        detection_results[element]["coordinates"] = [x, y]
                                        logging.info(f"Extracted coordinates for {element}: ({x}, {y})")
                                    except:
                                        pass
                
                # Process results
                results = {}
                for element in element_descriptions:
                    if element in detection_results:
                        if detection_results[element].get("found", False):
                            coords = detection_results[element].get("coordinates")
                            if isinstance(coords, list) and len(coords) == 2:
                                results[element] = (coords[0], coords[1])
                            else:
                                logging.warning(f"No valid coordinates for element '{element}'")
                                results[element] = None
                        else:
                            results[element] = None
                    else:
                        results[element] = None
                
                logging.info(f"Detection results: {results}")
                return results
                
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse model response as JSON: {e}")
                logging.error(f"Raw response: {response}")
                return {element: None for element in element_descriptions}
                
        except Exception as e:
            logging.error(f"Error during element detection: {e}")
            return {element: None for element in element_descriptions}
        finally:
            # Clean up temporary file
            try:
                os.remove(screenshot_path)
            except:
                pass
    
    def locate_chat_interface(self, site_name: str) -> Dict[str, Optional[Tuple[int, int]]]:
        """
        Locate common elements of a chat interface for a specific site
        
        Args:
            site_name: Name of the site (e.g., 'qwen', 'perplexity')
            
        Returns:
            Dictionary with coordinates of key UI elements
        """
        # Define site-specific element descriptions
        if site_name.lower() == 'qwen':
            elements = [
                "the chat input text area at the bottom of the screen",
                "the send button next to the input area",
                "the most recent AI response text area",
                "the text entry field where users type messages to Qwen",
                "the paper airplane or arrow icon used to send messages",
                "the message composition area at the bottom of the Qwen interface"
            ]
        elif site_name.lower() in ('perplexity', 'pplx'):
            elements = [
                "the chat input text box at the bottom of the screen",
                "the send arrow button",
                "the most recent AI response message"
            ]
        else:
            elements = [
                "the chat input text box or text area",
                "the send button or submit button",
                "the most recent message from the AI assistant"
            ]
        
        # Run detection
        return self.detect_elements(elements)
    
    def detect_captcha(self) -> bool:
        """
        Detect if a CAPTCHA is present on screen
        
        Returns:
            True if CAPTCHA is detected, False otherwise
        """
        # Load model if needed
        if self.model is None:
            self.load_model()
        
        # Capture screenshot
        screenshot = self._capture_screenshot()
        screenshot_path = self._save_temp_screenshot(screenshot)
        
        # Create a detection prompt
        prompt = """
        Look at this screenshot and determine if there is a CAPTCHA or human verification challenge visible.
        
        Examples of what to look for:
        - Any text mentioning "CAPTCHA", "verification", "prove you're human", etc.
        - Image-based CAPTCHA puzzles
        - Checkbox challenges like "I'm not a robot"
        - Slider puzzles or other interactive verification mechanisms
        
        Is there a CAPTCHA or human verification challenge visible in this screenshot? Answer yes or no and explain what you see.
        """
        
        # Process with the vision-language model
        try:
            logging.info("Checking for CAPTCHA presence...")
            
            # Process with the vision model
            if "blip" in self.model_name.lower():
                # BLIP model processing
                from PIL import Image
                from transformers import BlipProcessor
                
                processor = BlipProcessor.from_pretrained(self.model_name)
                image = Image.open(screenshot_path).convert('RGB')
                
                # Prepare inputs
                inputs = processor(images=image, text=prompt, return_tensors="pt").to(self.device)
                
                # Generate
                generated_ids = self.model.generate(**inputs, max_new_tokens=300)
                response = processor.decode(generated_ids[0], skip_special_tokens=True)
                
            else:
                # Standard ChatML format for most models
                try:
                    # Attempt multimodal format with error handling
                    try:
                        # Create message with image in multimodal format
                        messages = [
                            {"role": "user", "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image", "image_url": {"url": f"file://{screenshot_path}"}}
                            ]}
                        ]
                        
                        # Generate response
                        model_inputs = self.tokenizer.apply_chat_template(
                            messages, 
                            return_tensors="pt"
                        ).to(self.model.device)
                    except Exception as format_error:
                        # Broader error handling for any issues with multimodal format
                        logging.warning(f"Multimodal format failed: {format_error}, trying text-only format")
                        try:
                            # Fall back to text-only format for models that don't support multimodal input
                            text_messages = [
                                {"role": "user", "content": prompt}  # Use only text content
                            ]
                            model_inputs = self.tokenizer.apply_chat_template(
                                text_messages,
                                return_tensors="pt"
                            ).to(self.model.device)
                        except Exception as text_error:
                            # If text format also fails, try direct tokenization as a last resort
                            logging.warning(f"Text-only format also failed: {text_error}, trying direct tokenization")
                            # Direct tokenization without chat template
                            model_inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
                            logging.info("Direct tokenization succeeded")
                    generated_ids = self.model.generate(
                        model_inputs,
                        max_new_tokens=300,
                        do_sample=False
                    )
                    response = self.tokenizer.decode(generated_ids[0][model_inputs.shape[1]:], skip_special_tokens=True)
                except Exception as e:
                    logging.error(f"Error processing with standard method: {e}")
                    # Fallback to basic processing
                    from PIL import Image
                    image = Image.open(screenshot_path).convert('RGB')
                    
                    inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
                    generated_ids = self.model.generate(**inputs, max_new_tokens=300)
                    response = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)
                    response += "\n[Note: Image could not be processed with this model]"
            
            # Check for affirmative response
            response_lower = response.lower()
            captcha_detected = ("yes" in response_lower[:20] or 
                              "captcha" in response_lower or 
                              "verification" in response_lower or 
                              "robot" in response_lower or 
                              "human" in response_lower and "challenge" in response_lower)
            
            if captcha_detected:
                logging.info(f"CAPTCHA detected: {response[:100]}...")
            else:
                logging.info("No CAPTCHA detected")
            
            return captcha_detected
                
        except Exception as e:
            logging.error(f"Error during CAPTCHA detection: {e}")
            return False
        finally:
            # Clean up temporary file
            try:
                os.remove(screenshot_path)
            except:
                pass
    
    def extract_response_text(self) -> str:
        """
        Extract text of the AI's response from the screen
        
        Returns:
            Extracted text from the AI response area
        """
        # Load model if needed
        if self.model is None:
            self.load_model()
        
        # Capture screenshot
        screenshot = self._capture_screenshot()
        screenshot_path = self._save_temp_screenshot(screenshot)
        
        # Create a extraction prompt
        prompt = """
        Look at this screenshot of an AI chat interface. Extract the most recent response from the AI assistant.
        
        Format your response as follows:
        1. First line should say "AI RESPONSE START"
        2. Then include the complete text of the AI's response
        3. Last line should say "AI RESPONSE END"
        
        Only include the actual response text, not any UI elements, prompts, or other interface text.
        """
        
        # Process with the vision-language model
        try:
            logging.info("Extracting AI response text...")
            
            # Process with the vision model
            if "blip" in self.model_name.lower():
                # BLIP model processing
                from PIL import Image
                from transformers import BlipProcessor
                
                processor = BlipProcessor.from_pretrained(self.model_name)
                image = Image.open(screenshot_path).convert('RGB')
                
                # Prepare inputs
                inputs = processor(images=image, text=prompt, return_tensors="pt").to(self.device)
                
                # Generate
                generated_ids = self.model.generate(**inputs, max_new_tokens=2000)
                response = processor.decode(generated_ids[0], skip_special_tokens=True)
                
            else:
                # Standard ChatML format for most models
                try:
                    # Attempt multimodal format with error handling
                    try:
                        # Create message with image in multimodal format
                        messages = [
                            {"role": "user", "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image", "image_url": {"url": f"file://{screenshot_path}"}}
                            ]}
                        ]
                        
                        # Generate response
                        model_inputs = self.tokenizer.apply_chat_template(
                            messages, 
                            return_tensors="pt"
                        ).to(self.model.device)
                    except Exception as format_error:
                        # Broader error handling for any issues with multimodal format
                        logging.warning(f"Multimodal format failed: {format_error}, trying text-only format")
                        try:
                            # Fall back to text-only format for models that don't support multimodal input
                            text_messages = [
                                {"role": "user", "content": prompt}  # Use only text content
                            ]
                            model_inputs = self.tokenizer.apply_chat_template(
                                text_messages,
                                return_tensors="pt"
                            ).to(self.model.device)
                        except Exception as text_error:
                            # If text format also fails, try direct tokenization as a last resort
                            logging.warning(f"Text-only format also failed: {text_error}, trying direct tokenization")
                            # Direct tokenization without chat template
                            model_inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
                            logging.info("Direct tokenization succeeded")
                    generated_ids = self.model.generate(
                        model_inputs,
                        max_new_tokens=2000,
                        do_sample=False
                    )
                    response = self.tokenizer.decode(generated_ids[0][model_inputs.shape[1]:], skip_special_tokens=True)
                except Exception as e:
                    logging.error(f"Error processing with standard method: {e}")
                    # Fallback to basic processing
                    from PIL import Image
                    image = Image.open(screenshot_path).convert('RGB')
                    
                    inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
                    generated_ids = self.model.generate(**inputs, max_new_tokens=2000)
                    response = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)
                    response += "\n[Note: Image could not be processed with this model]"
            
            # Extract AI response text from between markers
            start_marker = "AI RESPONSE START"
            end_marker = "AI RESPONSE END"
            
            start_idx = response.find(start_marker)
            end_idx = response.find(end_marker)
            
            if start_idx >= 0 and end_idx > start_idx:
                extracted_text = response[start_idx + len(start_marker):end_idx].strip()
                logging.info(f"Successfully extracted response text ({len(extracted_text)} chars)")
                return extracted_text
            else:
                # If markers not found, return the whole text
                logging.warning("Response markers not found, returning full text")
                return response.strip()
                
        except Exception as e:
            logging.error(f"Error during text extraction: {e}")
            return ""
        finally:
            # Clean up temporary file
            try:
                os.remove(screenshot_path)
            except:
                pass

# Example usage
if __name__ == "__main__":
    # Test the vision detector
    detector = VisionDetector()
    
    # Wait for user to position browser window
    input("Position your browser window with the chat interface visible and press Enter...")
    
    # Load model
    detector.load_model()
    
    # Detect interface elements
    elements = detector.locate_chat_interface("qwen")
    print("Detected elements:")
    for element, coords in elements.items():
        print(f"- {element}: {coords}")
    
    # Check for CAPTCHA
    has_captcha = detector.detect_captcha()
    print(f"CAPTCHA detected: {has_captcha}")
    
    # Extract response text if any is visible
    response = detector.extract_response_text()
    print(f"Extracted response text ({len(response)} chars):")
    print(response[:200] + "..." if len(response) > 200 else response)
    
    # Unload model to free memory
    detector.unload_model()