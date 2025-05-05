#!/usr/bin/env python3
"""
Vision-enhanced site handlers for AI chat services
"""

import os
import sys
import time
import random
import logging
import pyautogui
import pyperclip
from PIL import ImageGrab, Image
from typing import Dict, List, Optional, Tuple, Union, Any
from abc import ABC, abstractmethod

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

# Import local modules
from .browser import Browser, BrowserType
from .human_input import HumanInput
from .vision_detection import VisionDetector
from .utils import save_screenshot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("site_vision.log"),
        logging.StreamHandler()
    ]
)

class VisionAIChatSite(ABC):
    """Vision-enhanced base class for AI chat site interaction"""
    
    def __init__(
        self, 
        browser: Browser,
        human: HumanInput,
        vision_detector: Optional[VisionDetector] = None,
        use_vision: bool = True,
        debug: bool = False
    ):
        """
        Initialize vision-enhanced AI chat site handler
        
        Args:
            browser: Browser instance for navigation
            human: HumanInput instance for interaction
            vision_detector: Optional pre-initialized vision detector
            use_vision: Whether to use vision detection
            debug: Enable debug mode
        """
        self.browser = browser
        self.human = human
        self.use_vision = use_vision
        self.debug = debug
        
        # UI element positions (to be populated by detection)
        self.input_field_pos = None
        self.send_button_pos = None
        self.response_area_pos = None
        
        # Create or use vision detector
        if use_vision:
            self.vision = vision_detector or VisionDetector()
            if vision_detector is None:
                # We created a new detector, so load the model
                self.vision.load_model()
        else:
            self.vision = None
        
        # Detect screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        logging.info(f"Screen dimensions: {self.screen_width}x{self.screen_height}")
    
    @abstractmethod
    def get_site_id(self) -> str:
        """Get site identifier"""
        pass
    
    @abstractmethod
    def get_site_url(self) -> str:
        """Get site URL"""
        pass
    
    def navigate(self) -> bool:
        """Navigate to the site"""
        result = self.browser.navigate_to_url(self.get_site_url())
        # Wait for page to load
        time.sleep(3)
        return result
    
    def detect_ui_elements(self, force_refresh: bool = False) -> bool:
        """
        Detect UI elements using vision model
        
        Args:
            force_refresh: Whether to force refresh the detection
            
        Returns:
            True if detection was successful
        """
        if not self.use_vision or self.vision is None:
            logging.warning("Vision detection not enabled or available")
            return False
        
        # Skip if we already have positions and not forcing refresh
        if not force_refresh and self.input_field_pos is not None:
            return True
        
        logging.info(f"Detecting UI elements for {self.get_site_id()}...")
        
        # Use vision detector to find elements
        elements = self.vision.locate_chat_interface(self.get_site_id())
        
        # Extract positions
        self.input_field_pos = elements.get("the chat input text area at the bottom of the screen")
        if self.input_field_pos is None:
            self.input_field_pos = elements.get("the chat input text box at the bottom of the screen")
        if self.input_field_pos is None:
            self.input_field_pos = elements.get("the chat input text box or text area")
            
        self.send_button_pos = elements.get("the send button next to the input area")
        if self.send_button_pos is None:
            self.send_button_pos = elements.get("the send arrow button")
        if self.send_button_pos is None:
            self.send_button_pos = elements.get("the send button or submit button")
            
        self.response_area_pos = elements.get("the most recent AI response text area")
        if self.response_area_pos is None:
            self.response_area_pos = elements.get("the most recent AI response message")
        if self.response_area_pos is None:
            self.response_area_pos = elements.get("the most recent message from the AI assistant")
        
        # Check if we found the input field at minimum
        success = self.input_field_pos is not None
        if success:
            logging.info(f"UI detection successful: input={self.input_field_pos}, send={self.send_button_pos}, response={self.response_area_pos}")
        else:
            logging.warning("Failed to detect input field position")
            
        # Take debug screenshot if enabled
        if self.debug:
            save_screenshot("ui_detection.png", directory="debug", compress=True, max_size_kb=500)
            
        return success
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in using UI detection"""
        # We consider the user logged in if we can detect the input field
        return self.detect_ui_elements()
    
    def detect_captcha(self) -> bool:
        """
        Detect if a CAPTCHA is present using vision model
        
        Returns:
            True if CAPTCHA is detected
        """
        if not self.use_vision or self.vision is None:
            logging.warning("Vision detection not enabled or available")
            return False
            
        logging.info("Checking for CAPTCHA...")
        result = self.vision.detect_captcha()
        
        if result:
            logging.warning("CAPTCHA detected")
            if self.debug:
                save_screenshot("captcha_detected.png", directory="debug", compress=True, max_size_kb=500)
        
        return result
    
    def wait_for_captcha_solution(self, timeout: int = 120) -> bool:
        """
        Wait for user to solve CAPTCHA
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if CAPTCHA appears solved, False if timeout
        """
        logging.info(f"Waiting for user to solve CAPTCHA (timeout: {timeout}s)")
        
        # Notify user
        print("\n" + "="*60)
        print("CAPTCHA DETECTED! Please solve the CAPTCHA manually.")
        print("The script will continue once the CAPTCHA is solved.")
        print("="*60 + "\n")
        
        # Check periodically if CAPTCHA is still present
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not self.detect_captcha():
                logging.info("CAPTCHA appears to be solved")
                time.sleep(2)  # Give a moment for page to update
                return True
            
            # Wait before checking again
            time.sleep(3)
            
            # Occasional human-like idle behavior
            if random.random() < 0.3:
                self.human.random_idle(random.uniform(0.5, 2.0))
        
        logging.warning(f"CAPTCHA solution timeout after {timeout}s")
        return False
    
    def send_message(self, message: str) -> bool:
        """
        Send a message using detected UI elements
        
        Args:
            message: Message to send
            
        Returns:
            True if message was sent successfully
        """
        # Detect UI elements if needed
        if not self.detect_ui_elements():
            logging.error("Failed to detect UI elements, cannot send message")
            return False
        
        # Move to input field
        logging.info(f"Clicking input field at {self.input_field_pos}")
        self.human.move_mouse(self.input_field_pos[0], self.input_field_pos[1])
        self.human.click()
        time.sleep(random.uniform(0.5, 1.0))
        
        # Type message
        logging.info(f"Typing message: {message[:50]}...")
        self.human.type_text(message)
        time.sleep(random.uniform(0.3, 0.8))
        
        # Use send button if we have it, otherwise use Enter key
        if self.send_button_pos:
            logging.info(f"Clicking send button at {self.send_button_pos}")
            self.human.move_mouse(self.send_button_pos[0], self.send_button_pos[1])
            self.human.click()
        else:
            logging.info("Using Enter key to send message")
            self.human.press_key('enter')
        
        # Wait a moment to verify message was sent
        time.sleep(2)
        
        # Take debug screenshot if enabled
        if self.debug:
            save_screenshot("after_send_message.png", directory="debug", compress=True, max_size_kb=500)
        
        return True
    
    def is_responding(self) -> bool:
        """
        Check if the AI is currently generating a response
        
        This is a simple implementation that checks if the input field is clickable
        Override in subclasses for site-specific behavior
        """
        # We consider the AI to be responding if we can't click in the input field
        if not self.input_field_pos:
            self.detect_ui_elements()
            if not self.input_field_pos:
                return False
        
        # Try clicking in the input field
        self.human.move_mouse(self.input_field_pos[0], self.input_field_pos[1])
        self.human.click()
        
        # Try typing a character - if we get a cursor, we can type
        # We need to be careful not to actually type anything
        
        # Check for other indicators like animation, this is site-specific
        # For now, assume it's done responding if we can click the input field
        return False
    
    def get_response(self) -> str:
        """
        Get the AI's response using vision extraction
        
        Returns:
            Extracted response text
        """
        # Wait for response to complete
        max_wait_time = 60  # Maximum wait time in seconds
        wait_start = time.time()
        
        logging.info("Waiting for response...")
        
        while self.is_responding():
            # Check timeout
            if time.time() - wait_start > max_wait_time:
                logging.warning(f"Timed out after waiting {max_wait_time}s for response")
                break
            
            # Wait with occasional human-like behavior
            time.sleep(random.uniform(1.0, 3.0))
            
            # Occasionally simulate idle human behavior
            if random.random() < 0.3:
                self.human.random_idle()
        
        logging.info("Response appears complete, extracting...")
        
        # Give UI a moment to fully render
        time.sleep(2)
        
        if self.use_vision and self.vision:
            # Use vision model to extract response text
            logging.info("Using vision model to extract response")
            response = self.vision.extract_response_text()
            
            # Check if we got a valid response
            if response and len(response) > 10:
                return response
                
            # If vision extraction failed, try clipboard method as fallback
            logging.warning("Vision extraction produced short or empty response, trying clipboard fallback")
            
        # Fallback: Try to copy response text to clipboard
        if self.response_area_pos:
            # Click the response area
            self.human.move_mouse(self.response_area_pos[0], self.response_area_pos[1])
            
            # Triple click to select all text in that element
            self.human.click(clicks=3, interval=0.1)
            time.sleep(0.5)
            
            # Copy selection
            if sys.platform == 'darwin':  # macOS
                pyautogui.hotkey('command', 'c')
            else:  # Windows/Linux
                pyautogui.hotkey('ctrl', 'c')
            
            time.sleep(0.5)
            
            # Get from clipboard
            response = pyperclip.paste()
            
            # Click away to clear selection
            self.human.move_mouse(10, 10)
            self.human.click()
            
            if response:
                return response
        
        logging.warning("Failed to extract response text")
        return "Failed to extract response"

class VisionQwenChatSite(VisionAIChatSite):
    """Vision-enhanced handler for chat.qwen.ai"""
    
    def get_site_id(self) -> str:
        return "qwen"
    
    def get_site_url(self) -> str:
        return "https://chat.qwen.ai/"
    
    def is_responding(self) -> bool:
        """Check if Qwen is currently generating a response"""
        # For Qwen, we can check if there's a blinking cursor in the input field
        # or if there's a loading animation
        
        # This is a placeholder - in a real implementation, we could use vision detection
        # to check for specific animations or UI states
        
        # Simplistic approach - if we can't click and type in the input field,
        # assume it's still responding
        if not self.input_field_pos:
            self.detect_ui_elements()
            if not self.input_field_pos:
                return False
                
        # Use vision detection to check for loading indicators
        if self.use_vision and self.vision:
            # We would need a custom prompt for the vision model to detect
            # if the AI is still generating a response
            pass
        
        # For now, default to parent implementation
        return super().is_responding()

class VisionPerplexitySite(VisionAIChatSite):
    """Vision-enhanced handler for perplexity.ai"""
    
    def get_site_id(self) -> str:
        return "perplexity"
    
    def get_site_url(self) -> str:
        return "https://www.perplexity.ai/"
    
    def is_responding(self) -> bool:
        """Check if Perplexity is currently generating a response"""
        # For Perplexity, there's typically an animation while it's responding
        
        # This is a placeholder - in a real implementation, we could use vision detection
        # to check for specific animations or UI states
        
        # Simplistic approach - if we can't click and type in the input field,
        # assume it's still responding
        if not self.input_field_pos:
            self.detect_ui_elements()
            if not self.input_field_pos:
                return False
                
        # Use vision detection to check for loading indicators
        if self.use_vision and self.vision:
            # We would need a custom prompt for the vision model to detect
            # if the AI is still generating a response
            pass
        
        # For now, default to parent implementation
        return super().is_responding()

# Factory function to create vision-enhanced site handlers
def create_vision_site_handler(
    site_name: str,
    browser: Browser,
    human: HumanInput,
    vision_detector: Optional[VisionDetector] = None,
    use_vision: bool = True,
    debug: bool = False
) -> VisionAIChatSite:
    """
    Create appropriate vision-enhanced site handler based on site name
    
    Args:
        site_name: Name of the site (qwen, perplexity, etc.)
        browser: Browser instance
        human: HumanInput instance
        vision_detector: Optional pre-initialized vision detector
        use_vision: Whether to use vision detection
        debug: Enable debug mode
        
    Returns:
        Appropriate VisionAIChatSite implementation
    """
    site_name = site_name.lower()
    
    if site_name == "qwen":
        return VisionQwenChatSite(browser, human, vision_detector, use_vision, debug)
    elif site_name in ("perplexity", "pplx"):
        return VisionPerplexitySite(browser, human, vision_detector, use_vision, debug)
    else:
        raise ValueError(f"Unsupported site: {site_name}")

# Example usage
if __name__ == "__main__":
    # Set up dependencies
    browser = Browser(BrowserType.CHROME)
    human = HumanInput()
    vision = VisionDetector()
    
    # Load model once and share it between handlers
    vision.load_model()
    
    # Create handler for Qwen with debug mode
    site = create_vision_site_handler(
        "qwen", 
        browser, 
        human, 
        vision_detector=vision,
        debug=True
    )
    
    # Navigate to site
    browser.launch_if_needed()
    site.navigate()
    
    # Detect UI elements
    if site.detect_ui_elements():
        print("UI elements detected successfully")
    else:
        print("Failed to detect UI elements")
    
    # Wait for user to handle login if needed
    if not site.is_logged_in():
        print("Please log in to the site manually...")
        input("Press Enter when logged in...")
    
    # Check for CAPTCHA
    if site.detect_captcha():
        site.wait_for_captcha_solution()
    
    # Send a test message
    site.send_message("What are the latest advancements in quantum computing?")
    
    # Get response
    response = site.get_response()
    print("\nResponse received:")
    print(response)
    
    # Clean up
    vision.unload_model()