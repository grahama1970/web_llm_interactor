#!/usr/bin/env python3
"""
Site-specific interaction handlers for various AI chat platforms
"""

import os
import sys
import time
import random
import logging
import pyautogui
import pyperclip
from PIL import ImageGrab, Image
import pytesseract
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Union, Any

# Import local modules
from .browser import Browser, BrowserType
from .human_input import HumanInput
from .utils import find_image_on_screen, wait_for_image, read_text_from_region

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("site.log"),
        logging.StreamHandler()
    ]
)

class AIChatSite(ABC):
    """Abstract base class for AI chat site interaction"""
    
    def __init__(
        self, 
        browser: Browser,
        human: HumanInput,
        resources_dir: str = "resources"
    ):
        """
        Initialize AI chat site handler
        
        Args:
            browser: Browser instance for navigation
            human: HumanInput instance for interaction
            resources_dir: Directory containing site-specific resources
        """
        self.browser = browser
        self.human = human
        self.resources_dir = resources_dir
        
        # Ensure resources directory exists
        os.makedirs(self.get_resource_path(""), exist_ok=True)
        
        # Detect screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        logging.info(f"Screen dimensions: {self.screen_width}x{self.screen_height}")
    
    def get_resource_path(self, filename: str) -> str:
        """Get full path to a resource file"""
        return os.path.join(self.resources_dir, self.get_site_id(), filename)
    
    @abstractmethod
    def get_site_id(self) -> str:
        """Get site identifier for resource loading"""
        pass
    
    @abstractmethod
    def get_site_url(self) -> str:
        """Get site URL"""
        pass
    
    def navigate(self) -> bool:
        """Navigate to the site"""
        return self.browser.navigate_to_url(self.get_site_url())
    
    @abstractmethod
    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        pass
    
    @abstractmethod
    def detect_input_field(self) -> Optional[Tuple[int, int]]:
        """Detect and return coordinates of the input field"""
        pass
    
    @abstractmethod
    def send_message(self, message: str) -> bool:
        """Send a message to the AI"""
        pass
    
    @abstractmethod
    def is_responding(self) -> bool:
        """Check if the AI is currently generating a response"""
        pass
    
    @abstractmethod
    def get_response(self) -> str:
        """Get the AI's response after it's done generating"""
        pass
    
    def detect_captcha(self) -> bool:
        """
        Detect if a CAPTCHA is present
        Returns True if CAPTCHA is detected
        """
        # Take screenshot
        screenshot = ImageGrab.grab()
        
        # Convert to text using OCR
        text = pytesseract.image_to_string(screenshot).lower()
        
        # Look for CAPTCHA indicators
        captcha_indicators = [
            'captcha', 'robot', 'verify', 'human', 
            'security check', 'challenge', 'prove',
            'not a robot', 'i am human'
        ]
        
        for indicator in captcha_indicators:
            if indicator in text:
                logging.warning(f"CAPTCHA detected: Found '{indicator}' on screen")
                return True
        
        # Check for CAPTCHA images if available
        captcha_images = [
            f for f in os.listdir(self.get_resource_path(""))
            if f.startswith("captcha_") and f.endswith((".png", ".jpg"))
        ]
        
        for image_file in captcha_images:
            image_path = self.get_resource_path(image_file)
            try:
                if find_image_on_screen(image_path):
                    logging.warning(f"CAPTCHA detected: Found image {image_file}")
                    return True
            except Exception as e:
                logging.error(f"Error checking CAPTCHA image {image_file}: {e}")
        
        return False
    
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
    
    def chat_with_random_delay(self, messages: List[str], delay_range: Tuple[int, int] = (20, 60)) -> List[str]:
        """
        Send multiple messages with random delays between them
        
        Args:
            messages: List of messages to send
            delay_range: Range of delays between messages in seconds
            
        Returns:
            List of responses from the AI
        """
        responses = []
        
        for i, message in enumerate(messages):
            logging.info(f"Sending message {i+1}/{len(messages)}")
            
            # Navigate if first message
            if i == 0:
                self.navigate()
                time.sleep(3)
                
                # Check for CAPTCHA
                if self.detect_captcha():
                    if not self.wait_for_captcha_solution():
                        logging.error("Failed to get past CAPTCHA")
                        break
            
            # Send message
            success = self.send_message(message)
            if not success:
                logging.error(f"Failed to send message: {message}")
                break
            
            # Wait for and get response
            response = self.get_response()
            responses.append(response)
            
            # Add random delay between messages
            if i < len(messages) - 1:
                delay = random.randint(delay_range[0], delay_range[1])
                logging.info(f"Waiting {delay}s before next message")
                
                # Break delay into smaller chunks with idle behavior
                remaining = delay
                while remaining > 0:
                    chunk = min(remaining, random.randint(5, 15))
                    time.sleep(chunk)
                    
                    # Occasional human-like behavior during wait
                    self.human.random_idle(random.uniform(1.0, 3.0))
                    
                    remaining -= chunk
        
        return responses

class QwenChatSite(AIChatSite):
    """Handler for chat.qwen.ai"""
    
    def get_site_id(self) -> str:
        return "qwen"
    
    def get_site_url(self) -> str:
        return "https://chat.qwen.ai/"
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in to Qwen"""
        # Look for login button
        login_button = self.get_resource_path("login_button.png")
        
        if os.path.exists(login_button):
            # If login button is found, user is not logged in
            return not bool(find_image_on_screen(login_button))
        
        # Alternative detection: look for user avatar
        user_avatar = self.get_resource_path("user_avatar.png")
        if os.path.exists(user_avatar):
            return bool(find_image_on_screen(user_avatar))
        
        # Default to checking if input field is detected
        return self.detect_input_field() is not None
    
    def detect_input_field(self) -> Optional[Tuple[int, int]]:
        """Detect and return coordinates of the input field"""
        # Try to find input field image
        input_field = self.get_resource_path("input_field.png")
        
        # Check if resource exists
        if os.path.exists(input_field):
            location = find_image_on_screen(input_field)
            if location:
                logging.info(f"Found input field at {location}")
                return location
        
        # Fallback: try to find based on fixed positions
        # This assumes a certain screen layout and should be customized
        # These are placeholder values - replace with actual positions based on testing
        x_pos = int(self.screen_width * 0.5)
        y_pos = int(self.screen_height * 0.9)
        
        logging.info(f"Using fallback input position: {x_pos}, {y_pos}")
        
        # Verify this position by clicking and checking if cursor blinks
        # This would require additional logic
        
        return (x_pos, y_pos)
    
    def send_message(self, message: str) -> bool:
        """Send a message to Qwen"""
        input_pos = self.detect_input_field()
        if not input_pos:
            logging.error("Could not find input field")
            return False
        
        # Move to input field
        self.human.move_mouse(input_pos[0], input_pos[1])
        self.human.click()
        time.sleep(random.uniform(0.5, 1.0))
        
        # Type message
        self.human.type_text(message)
        time.sleep(random.uniform(0.3, 0.8))
        
        # Press Enter to send
        self.human.press_key('enter')
        
        # Verify message was sent
        # Qwen typically shows a loading indicator when generating response
        time.sleep(2)  # Wait for UI to update
        
        return True
    
    def is_responding(self) -> bool:
        """Check if Qwen is currently generating a response"""
        # Look for loading indicator
        loading_icon = self.get_resource_path("loading_icon.png")
        
        if os.path.exists(loading_icon):
            return bool(find_image_on_screen(loading_icon))
        
        # Fallback: check for cursor (will be blinking if input is enabled)
        input_field = self.detect_input_field()
        if input_field:
            self.human.move_mouse(input_field[0], input_field[1])
            self.human.click()
            
            # If we can type, the AI is probably done responding
            return False
        
        # If we can't determine, assume it's still responding
        return True
    
    def get_response(self) -> str:
        """Wait for and get Qwen's response"""
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
        
        logging.info("Response appears complete, capturing...")
        
        # Give UI a moment to fully render
        time.sleep(2)
        
        # Select all to get response
        input_field = self.detect_input_field()
        if input_field:
            # Move just above the input field to find the response
            response_y = input_field[1] - 200  # Adjust as needed
            self.human.move_mouse(input_field[0], response_y)
            
            # Triple click to select paragraph
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
            
            return response
        
        # Fallback: use OCR to capture response
        # Take screenshot of the approximate response area
        screenshot = ImageGrab.grab()
        
        # The response area dimensions will vary by site layout
        # These are placeholder values - replace with actual positions
        response_left = int(self.screen_width * 0.2)
        response_top = int(self.screen_height * 0.3)
        response_right = int(self.screen_width * 0.8)
        response_bottom = int(self.screen_height * 0.8)
        
        response_area = screenshot.crop((
            response_left, response_top, response_right, response_bottom
        ))
        
        # Use OCR to extract text
        response = pytesseract.image_to_string(response_area)
        
        return response.strip()

class PerplexitySite(AIChatSite):
    """Handler for perplexity.ai"""
    
    def get_site_id(self) -> str:
        return "perplexity"
    
    def get_site_url(self) -> str:
        return "https://www.perplexity.ai/"
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in to Perplexity"""
        # Look for login button or user avatar
        login_button = self.get_resource_path("login_button.png")
        user_avatar = self.get_resource_path("user_avatar.png")
        
        if os.path.exists(login_button):
            return not bool(find_image_on_screen(login_button))
        
        if os.path.exists(user_avatar):
            return bool(find_image_on_screen(user_avatar))
        
        # Default to checking if input field is detected
        return self.detect_input_field() is not None
    
    def detect_input_field(self) -> Optional[Tuple[int, int]]:
        """Detect and return coordinates of the input field"""
        # Try to find input field image
        input_field = self.get_resource_path("input_field.png")
        
        # Check if resource exists
        if os.path.exists(input_field):
            location = find_image_on_screen(input_field)
            if location:
                logging.info(f"Found input field at {location}")
                return location
        
        # Perplexity typically has the input at bottom center
        x_pos = int(self.screen_width * 0.5)
        y_pos = int(self.screen_height * 0.9)
        
        logging.info(f"Using fallback input position: {x_pos}, {y_pos}")
        return (x_pos, y_pos)
    
    def send_message(self, message: str) -> bool:
        """Send a message to Perplexity"""
        input_pos = self.detect_input_field()
        if not input_pos:
            logging.error("Could not find input field")
            return False
        
        # Move to input field
        self.human.move_mouse(input_pos[0], input_pos[1])
        self.human.click()
        time.sleep(random.uniform(0.5, 1.0))
        
        # Type message
        self.human.type_text(message)
        time.sleep(random.uniform(0.3, 0.8))
        
        # Look for send button
        send_button = self.get_resource_path("send_button.png")
        send_button_found = False
        
        if os.path.exists(send_button):
            send_location = find_image_on_screen(send_button)
            if send_location:
                self.human.move_mouse(send_location[0], send_location[1])
                self.human.click()
                send_button_found = True
        
        # If no send button found, use Enter key
        if not send_button_found:
            self.human.press_key('enter')
        
        # Verify message was sent
        time.sleep(2)  # Wait for UI to update
        
        return True
    
    def is_responding(self) -> bool:
        """Check if Perplexity is currently generating a response"""
        # Look for loading indicator
        loading_icon = self.get_resource_path("loading_icon.png")
        
        if os.path.exists(loading_icon):
            return bool(find_image_on_screen(loading_icon))
        
        # Perplexity often shows a pulsing cursor or animated dots
        # Could try to detect this through image differencing
        
        # Check if input field is disabled (Perplexity disables input while responding)
        input_field = self.detect_input_field()
        if input_field:
            # Try typing a single character
            self.human.move_mouse(input_field[0], input_field[1])
            self.human.click()
            
            # If we can type, the AI is probably done responding
            return False
        
        # Default: assume still responding
        return True
    
    def get_response(self) -> str:
        """Wait for and get Perplexity's response"""
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
            
            # Occasionally simulate idle behavior
            if random.random() < 0.3:
                self.human.random_idle()
        
        logging.info("Response appears complete, capturing...")
        
        # Give UI a moment to fully render
        time.sleep(2)
        
        # Perplexity's response is typically above the input area
        # Try selecting from the latest response bubble
        
        input_field = self.detect_input_field()
        if input_field:
            # Move up from input field to locate response
            response_y = input_field[1] - 150  # Adjust based on testing
            self.human.move_mouse(input_field[0], response_y)
            
            # Triple click to select paragraph
            self.human.click(clicks=3, interval=0.1)
            time.sleep(0.5)
            
            # Try dragging to select more text if available
            self.human.click()  # Single click to position cursor
            pyautogui.dragRel(0, -300, duration=1.0)  # Drag upward to select text
            
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
            
            return response
        
        # Fallback: use OCR
        screenshot = ImageGrab.grab()
        
        # Response area for Perplexity
        response_left = int(self.screen_width * 0.2)
        response_top = int(self.screen_height * 0.3)
        response_right = int(self.screen_width * 0.8)
        response_bottom = int(self.screen_height * 0.8)
        
        response_area = screenshot.crop((
            response_left, response_top, response_right, response_bottom
        ))
        
        # Save for debugging
        debug_path = os.path.join("debug", "perplexity_response.png")
        os.makedirs("debug", exist_ok=True)
        response_area.save(debug_path)
        
        # Use OCR to extract text
        response = pytesseract.image_to_string(response_area)
        
        return response.strip()

# Factory function to create site handlers
def create_site_handler(
    site_name: str,
    browser: Browser,
    human: HumanInput,
    resources_dir: str = "resources"
) -> AIChatSite:
    """
    Create appropriate site handler based on site name
    
    Args:
        site_name: Name of the site (qwen, perplexity, etc.)
        browser: Browser instance
        human: HumanInput instance
        resources_dir: Directory for site resources
        
    Returns:
        Appropriate AIChatSite implementation
    """
    site_name = site_name.lower()
    
    if site_name == "qwen":
        return QwenChatSite(browser, human, resources_dir)
    elif site_name in ("perplexity", "pplx"):
        return PerplexitySite(browser, human, resources_dir)
    else:
        raise ValueError(f"Unsupported site: {site_name}")

# Example usage
if __name__ == "__main__":
    # Set up dependencies
    browser = Browser(BrowserType.CHROME)
    human = HumanInput()
    
    # Create handler for Qwen
    site = create_site_handler("qwen", browser, human)
    
    # Navigate to site
    browser.launch_if_needed()
    site.navigate()
    
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