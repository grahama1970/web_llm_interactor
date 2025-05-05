"""
UI automation module that combines browser control, human-like input, and vision-based UI detection.

This module integrates the browser management, human-like input simulation, and
Qwen-VL vision capabilities into a cohesive system for interacting with AI chat sites.
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
from pathlib import Path

# Import local modules
from .browser import Browser, BrowserType
from .human_input import HumanInput
from .qwen_processor import QwenVLProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ui_automation.log"),
        logging.StreamHandler()
    ]
)

class UIChatAutomation:
    """
    High-level class that integrates browser control, human input simulation,
    and vision-based UI detection for automating AI chat interactions.
    """
    
    def __init__(
        self,
        site_name: str,
        browser_type: Union[str, BrowserType] = BrowserType.CHROME,
        use_vision: bool = True,
        debug: bool = False,
        qwen_model: str = "Qwen/Qwen2.5-VL-7B"
    ):
        """
        Initialize UI automation for chat interactions
        
        Args:
            site_name: Name of the site to automate (e.g., 'qwen', 'perplexity')
            browser_type: Type of browser to use
            use_vision: Whether to use vision-based UI detection
            debug: Enable debug mode with screenshots
            qwen_model: Vision model to use for UI detection
        """
        self.site_name = site_name.lower()
        self.debug = debug
        self.use_vision = use_vision
        
        # Initialize components
        self.browser = Browser(browser_type)
        self.human = HumanInput()
        
        # Only initialize vision if enabled
        self.vision = QwenVLProcessor(qwen_model) if use_vision else None
        
        # UI element positions and dimensions (to be populated by detection)
        self.ui_elements = {
            "input_field": {"center": None, "box": None},
            "send_button": {"center": None, "box": None},
            "response_area": {"center": None, "box": None}
        }
        
        # Site-specific information
        self.site_url = self._get_site_url()
        
        # Status flags
        self.is_initialized = False
        self.is_logged_in = False
        
        # Screen dimensions for fallback
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Debug info
        logging.info(f"Initialized UI automation for {self.site_name} site")
        if self.debug:
            os.makedirs("debug", exist_ok=True)
    
    def _get_site_url(self) -> str:
        """Get the URL for the configured site"""
        if self.site_name == "qwen":
            return "https://chat.qwen.ai/"
        elif self.site_name in ("perplexity", "pplx"):
            return "https://www.perplexity.ai/"
        elif self.site_name == "claude":
            return "https://claude.ai/"
        elif self.site_name == "chatgpt":
            return "https://chat.openai.com/"
        else:
            raise ValueError(f"Unknown site: {self.site_name}")
    
    def initialize(self) -> bool:
        """
        Initialize the automation by detecting browser and navigating to site
        
        Returns:
            True if initialization was successful
        """
        # Find existing browser or launch new one
        if not self.browser.find_process():
            logging.info("No existing browser found, launching new instance")
            if not self.browser.launch_if_needed():
                logging.error("Failed to launch browser")
                return False
        else:
            logging.info("Found existing browser process")
            
        # Navigate to the site
        logging.info(f"Navigating to {self.site_url}")
        if not self.browser.navigate_to_url(self.site_url):
            logging.error(f"Failed to navigate to {self.site_url}")
            return False
            
        # Wait for page to load
        time.sleep(3)
        
        # Detect UI elements if vision is enabled
        if self.use_vision and self.vision:
            self.detect_ui_elements()
            
        self.is_initialized = True
        return True
    
    def detect_ui_elements(self) -> bool:
        """
        Detect UI elements using vision model
        
        Returns:
            True if elements were detected successfully
        """
        if not self.use_vision or not self.vision:
            logging.warning("Vision detection not enabled")
            return False
            
        # Take screenshot for detection
        screenshot = ImageGrab.grab()
        
        if self.debug:
            # Save screenshot for debugging
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            debug_path = os.path.join("debug", f"detect_{timestamp}.png")
            screenshot.save(debug_path)
            logging.info(f"Saved debug screenshot to {debug_path}")
        
        # Detect UI elements
        logging.info(f"Detecting UI elements for {self.site_name}")
        elements = self.vision.detect_ui_elements(screenshot, self.site_name)
        
        # Update internal state
        self.ui_elements = elements
        
        # Use fallback positions if detection failed
        if self.ui_elements["input_field"]["center"] is None:
            if self.site_name == "qwen":
                # Set fallback for Qwen chat input (bottom center)
                center_pos = (self.screen_width // 2, int(self.screen_height * 0.9))
                # Approximate box dimensions for the input field
                width = int(self.screen_width * 0.7)  # 70% of screen width
                height = 50  # Default height for input field
                box = [
                    center_pos[0] - width//2,  # x1 (left)
                    center_pos[1] - height//2,  # y1 (top)
                    center_pos[0] + width//2,  # x2 (right)
                    center_pos[1] + height//2   # y2 (bottom)
                ]
                self.ui_elements["input_field"]["center"] = center_pos
                self.ui_elements["input_field"]["box"] = box
                logging.info(f"Using fallback position for Qwen input: {self.ui_elements['input_field']}")
            elif self.site_name in ("perplexity", "pplx"):
                # Set fallback for Perplexity chat input (bottom center)
                center_pos = (self.screen_width // 2, int(self.screen_height * 0.9))
                # Approximate box dimensions for the input field
                width = int(self.screen_width * 0.7)  # 70% of screen width
                height = 50  # Default height for input field
                box = [
                    center_pos[0] - width//2,  # x1 (left)
                    center_pos[1] - height//2,  # y1 (top)
                    center_pos[0] + width//2,  # x2 (right)
                    center_pos[1] + height//2   # y2 (bottom)
                ]
                self.ui_elements["input_field"]["center"] = center_pos
                self.ui_elements["input_field"]["box"] = box
                logging.info(f"Using fallback position for Perplexity input: {self.ui_elements['input_field']}")
        
        # For Qwen, set fallback values for response area if not detected
        if self.site_name == "qwen" and self.ui_elements["response_area"]["center"] is None:
            # We know Qwen puts the response area in the middle of the chat window
            center_pos = (self.screen_width // 2, int(self.screen_height * 0.4))
            # Approximate box for the response area - size based on typical chat UIs
            width = int(self.screen_width * 0.6)  # 60% of screen width
            height = int(self.screen_height * 0.4)  # 40% of screen height
            box = [
                center_pos[0] - width//2,  # x1 (left)
                center_pos[1] - height//2,  # y1 (top)
                center_pos[0] + width//2,  # x2 (right)
                center_pos[1] + height//2   # y2 (bottom)
            ]
            self.ui_elements["response_area"]["center"] = center_pos
            self.ui_elements["response_area"]["box"] = box
            logging.info(f"Using fallback position for Qwen response area: {self.ui_elements['response_area']}")
        
        # Check if we found the critical elements
        success = self.ui_elements["input_field"]["center"] is not None
        if success:
            logging.info(f"UI detection successful: {self.ui_elements}")
        else:
            logging.warning("Failed to detect input field")
            
        return success
    
    def check_login_status(self, wait_for_login: bool = False) -> bool:
        """
        Check if user is logged in
        
        Args:
            wait_for_login: Whether to wait for user to log in manually
            
        Returns:
            True if logged in, False otherwise
        """
        # With vision, we consider the user logged in if we can detect the input field
        if self.use_vision and self.vision:
            logged_in = self.ui_elements["input_field"] is not None
            
            # If detection failed, try again
            if not logged_in:
                logged_in = self.detect_ui_elements()
        else:
            # Without vision, we assume logged in if initialized
            logged_in = self.is_initialized
        
        # If not logged in and waiting is requested
        if not logged_in and wait_for_login:
            print("\n" + "="*60)
            print("You don't appear to be logged in. Please log in manually.")
            print("The script will continue once you press Enter...")
            print("="*60)
            input("\nPress Enter when you've completed the login process...")
            
            # Try detecting UI elements again after login
            if self.use_vision and self.vision:
                logged_in = self.detect_ui_elements()
            else:
                logged_in = True  # Assume success without vision
        
        self.is_logged_in = logged_in
        return logged_in
    
    def detect_captcha(self) -> bool:
        """
        Check if a CAPTCHA is present on the page
        
        Returns:
            True if CAPTCHA detected, False otherwise
        """
        if not self.use_vision or not self.vision:
            logging.warning("Vision detection not enabled, cannot check for CAPTCHA")
            return False
            
        # Take screenshot for detection
        screenshot = ImageGrab.grab()
        
        if self.debug:
            # Save screenshot for debugging
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            debug_path = os.path.join("debug", f"captcha_check_{timestamp}.png")
            screenshot.save(debug_path)
        
        # Detect CAPTCHA
        captcha_present, description = self.vision.detect_captcha(screenshot)
        
        if captcha_present:
            logging.warning(f"CAPTCHA detected: {description}")
            if self.debug:
                debug_path = os.path.join("debug", f"captcha_detected_{timestamp}.png")
                screenshot.save(debug_path)
        
        return captcha_present
    
    def wait_for_captcha_solution(self, timeout: int = 120) -> bool:
        """
        Wait for user to solve CAPTCHA manually
        
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
                
                # Wait a moment for page to update
                time.sleep(2)
                
                # Re-detect UI elements as they might have changed
                if self.use_vision and self.vision:
                    self.detect_ui_elements()
                    
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
        Send a message to the AI chat
        
        Args:
            message: Message to send
            
        Returns:
            True if message was sent successfully
        """
        # Check if we have the input field position
        if not self.ui_elements["input_field"]["center"]:
            logging.error("Input field position unknown, cannot send message")
            
            # Try to detect UI elements
            if self.use_vision and self.vision:
                if not self.detect_ui_elements():
                    return False
            else:
                # Use fallback position for Qwen
                if self.site_name == "qwen":
                    # Qwen chat interface has the input field in the center of the chat box
                    # Looking at the screenshots, we need to click directly in the placeholder text "How can I help you today?"
                    center_y = int(self.screen_height * 0.41)  # The placeholder text is clearly visible in screenshots
                    center_x = self.screen_width // 2  # Center of the screen horizontally
                    
                    # Set center position
                    self.ui_elements["input_field"]["center"] = (center_x, center_y)
                    
                    # Create bounding box for input field
                    width = int(self.screen_width * 0.7)  # 70% of screen width
                    height = 50  # Default height for input field
                    self.ui_elements["input_field"]["box"] = [
                        center_x - width//2,
                        center_y - height//2,
                        center_x + width//2,
                        center_y + height//2
                    ]
                    
                    # Send button is on the right side of the input field
                    send_x = int(self.screen_width * 0.75)  # 75% across
                    self.ui_elements["send_button"]["center"] = (send_x, center_y)
                    
                    # Response area is above the input field
                    response_y = center_y - 150
                    self.ui_elements["response_area"]["center"] = (center_x, response_y)
                    
                    # Create bounding box for response area
                    resp_width = int(self.screen_width * 0.7)
                    resp_height = int(self.screen_height * 0.3)
                    self.ui_elements["response_area"]["box"] = [
                        center_x - resp_width//2,
                        response_y - resp_height//2,
                        center_x + resp_width//2,
                        response_y + resp_height//2
                    ]
                    
                    logging.info(f"Using fallback position for Qwen input: {self.ui_elements['input_field']}")
                    logging.info(f"Using fallback position for Qwen send button: {self.ui_elements['send_button']}")
                    logging.info(f"Using fallback position for Qwen response area: {self.ui_elements['response_area']}")
                else:
                    return False
        
        # Get positions for interaction
        input_pos = self.ui_elements["input_field"]["center"]
        
        # Move to input field
        logging.info(f"Clicking input field at {input_pos}")
        self.human.move_mouse(input_pos[0], input_pos[1])
        self.human.click()
        time.sleep(random.uniform(0.5, 1.0))
        
        # Clear any placeholder text if needed (like "How can I help you today?")
        if self.site_name == "qwen":
            # Triple click to select the entire field (more reliable than Ctrl+A/Cmd+A)
            self.human.click(clicks=3, interval=0.1)
            time.sleep(0.3)
            
            # Press Delete or Backspace to clear
            self.human.press_key('delete')
            time.sleep(0.3)
            
            # Also try backspace as a fallback
            self.human.press_key('backspace')
            time.sleep(random.uniform(0.3, 0.5))
        
        # Type message
        logging.info(f"Typing message: {message[:50]}..." if len(message) > 50 else f"Typing message: {message}")
        
        # For Qwen, try direct typing instead of paste
        if self.site_name == "qwen":
            self.human.type_text(message)
        else:
            # Use paste_text for other sites
            self.human.paste_text(message)
            
        time.sleep(random.uniform(0.3, 0.8))
        
        # Take debug screenshot after pasting text
        if self.debug:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            debug_path = os.path.join("debug", f"after_paste_{timestamp}.png")
            ImageGrab.grab().save(debug_path)
            logging.info(f"Saved screenshot after pasting text to {debug_path}")
        
        # Use send button if detected, otherwise press Enter
        if self.ui_elements["send_button"]["center"]:
            send_pos = self.ui_elements["send_button"]["center"]
            logging.info(f"Clicking send button at {send_pos}")
            self.human.move_mouse(send_pos[0], send_pos[1])
            self.human.click()
        else:
            logging.info("Using Enter key to send message")
            self.human.press_key('enter')
        
        # Take debug screenshot if enabled
        if self.debug:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            debug_path = os.path.join("debug", f"after_send_{timestamp}.png")
            ImageGrab.grab().save(debug_path)
        
        # Verify message was sent (wait for response)
        time.sleep(2)
        
        return True
    
    def is_ai_responding(self) -> bool:
        """
        Check if the AI is currently generating a response
        
        Returns:
            True if the AI appears to be responding, False otherwise
        """
        # If we have vision detection, use it to check for animation indicators
        if self.use_vision and self.vision:
            # This would require a specialized prompt for detecting animation
            # For now, we'll use a simple heuristic based on the input field
            
            # If we can click and type in the input field, assume it's not responding
            if self.ui_elements["input_field"]:
                try:
                    # Move to input field
                    self.human.move_mouse(
                        self.ui_elements["input_field"][0], 
                        self.ui_elements["input_field"][1]
                    )
                    self.human.click()
                    
                    # If we got a cursor, assume AI is done responding
                    return False
                except:
                    pass
        
        # For sites like Perplexity, the input is often disabled while responding
        # For now, a simple approach is to check if Enter key works in the input field
        
        # Future: Implement more sophisticated detection of "AI is typing" indicators
        
        # Default: assume not responding to avoid getting stuck
        return False
    
    def get_response(self, sent_message: Optional[str] = None) -> str:
        """
        Wait for and extract the AI's response
        
        Args:
            sent_message: The message that was sent (for filtering response)
            
        Returns:
            Extracted response text
        """
        # Wait for response to complete
        max_wait_time = 60  # Maximum wait time in seconds
        wait_start = time.time()
        
        logging.info("Waiting for response...")
        
        while self.is_ai_responding():
            # Check timeout
            if time.time() - wait_start > max_wait_time:
                logging.warning(f"Timed out after waiting {max_wait_time}s for response")
                break
            
            # Wait with occasional human-like behavior
            time.sleep(random.uniform(1.0, 3.0))
            
            # Occasionally simulate idle behavior
            if random.random() < 0.3:
                self.human.random_idle()
        
        logging.info("Response appears complete, extracting...")
        
        # Give UI a moment to fully render
        time.sleep(2)
        
        # Take screenshot for extraction
        screenshot = ImageGrab.grab()
        
        if self.debug:
            # Save screenshot for debugging
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            debug_path = os.path.join("debug", f"response_{timestamp}.png")
            screenshot.save(debug_path)
        
        # Extract response using vision if available
        if self.use_vision and self.vision:
            logging.info("Using vision model to extract response")
            response = self.vision.extract_response_text(screenshot)
            
            # Check if we got a valid response
            if response and len(response) > 10:
                return response
                
            # If vision extraction failed, try clipboard method as fallback
            logging.warning("Vision extraction produced short response, trying clipboard fallback")
        
        # Fallback: Try to copy response text to clipboard
        if self.ui_elements["response_area"]["center"]:
            # For all sites, use a more reliable select-all approach
            # First click in the response area
            response_pos = self.ui_elements["response_area"]["center"]
            
            if self.ui_elements["response_area"]["box"]:
                # If we have a box, click in the center of the response area
                logging.info(f"Using response area bounding box: {self.ui_elements['response_area']['box']}")
                x1, y1, x2, y2 = self.ui_elements["response_area"]["box"]
                
                # Click in the general center of the response area
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                self.human.move_mouse(center_x, center_y)
            else:
                # If no box, use the center point
                self.human.move_mouse(response_pos[0], response_pos[1])
            
            # Click to position cursor in the response text
            self.human.click()
            time.sleep(0.5)
            
            # First try triple clicking to select a paragraph as a fallback
            self.human.click(clicks=3, interval=0.1)
            time.sleep(0.5)
            
            # Then use keyboard shortcut for Select All
            logging.info("Using Select All keyboard shortcut")
            if sys.platform == 'darwin':  # macOS
                pyautogui.hotkey('command', 'a')
            else:  # Windows/Linux
                pyautogui.hotkey('ctrl', 'a')
            
            time.sleep(0.5)
            
            # Copy selection
            if sys.platform == 'darwin':  # macOS
                pyautogui.hotkey('command', 'c')
            else:  # Windows/Linux
                pyautogui.hotkey('ctrl', 'c')
            
            time.sleep(0.5)
            
            # Get from clipboard
            response = pyperclip.paste()
            logging.info(f"Clipboard content length: {len(response)}")
            if len(response) > 100:
                logging.info(f"Clipboard preview: {response[:100]}...")
            else:
                logging.info(f"Clipboard content: {response}")
            
            # Process response to exclude the query
            if response and self.site_name == "qwen" and sent_message:
                # If the response contains the original query, try to extract just the response part
                if sent_message in response:
                    parts = response.split(sent_message, 1)
                    if len(parts) > 1 and parts[1].strip():
                        response = parts[1].strip()
                        logging.info(f"Extracted response part after query")
            
            # Click away to clear selection
            self.human.move_mouse(10, 10)
            self.human.click()
            
            if response:
                return response
        
        logging.warning("Failed to extract response text through all methods")
        return "Failed to extract response"
    
    def cleanup(self) -> None:
        """Clean up resources when done"""
        # Unload vision model if it was loaded
        if self.use_vision and self.vision:
            self.vision.unload_model()
            
        logging.info("Cleanup completed")

# Example usage
if __name__ == "__main__":
    # Enable debug mode for testing
    automation = UIChatAutomation("qwen", debug=True)
    
    # Initialize automation
    if automation.initialize():
        print("Initialization successful")
        
        # Check login status
        if automation.check_login_status(wait_for_login=True):
            print("Logged in successfully")
            
            # Check for CAPTCHA
            if automation.detect_captcha():
                print("CAPTCHA detected, waiting for solution...")
                if not automation.wait_for_captcha_solution():
                    print("CAPTCHA solution timed out")
                    automation.cleanup()
                    exit(1)
            
            # Send test message
            print("Sending test message...")
            if automation.send_message("What are the latest advancements in quantum computing?"):
                
                # Get response
                print("Waiting for response...")
                response = automation.get_response()
                
                print("\nResponse received:")
                print(response[:200] + "..." if len(response) > 200 else response)
        else:
            print("Not logged in")
    else:
        print("Initialization failed")
    
    # Clean up
    automation.cleanup()