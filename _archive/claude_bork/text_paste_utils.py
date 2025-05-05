#!/usr/bin/env python3
"""
Utility functions for pasting text into chat interfaces using vision detection
"""

import os
import sys
import time
import random
import logging
import pyautogui
import pyperclip
from typing import Dict, List, Optional, Tuple, Union, Any

# Try to import from local directory first, then from examples
try:
    from .human_input import HumanInput
    from .vision_detection import VisionDetector
    from .image_processing_utils import compress_image, compress_image_object
    from .utils import save_screenshot
except ImportError:
    try:
        # Also try importing from examples directory
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'examples'))
        from image_processing_utils import compress_image, compress_image_object
    except ImportError:
        logging.warning("Could not import required modules, functionality may be limited")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("text_paste.log"),
        logging.StreamHandler()
    ]
)

class TextPaster:
    """Handles pasting text into chat windows using vision detection"""
    
    def __init__(
        self, 
        human: HumanInput,
        vision_detector: Optional[VisionDetector] = None,
        debug: bool = False
    ):
        """
        Initialize text paster
        
        Args:
            human: HumanInput instance for interaction
            vision_detector: Optional pre-initialized vision detector
            debug: Enable debug mode with screenshots
        """
        self.human = human
        self.debug = debug
        
        # Create or use vision detector
        if vision_detector:
            self.vision = vision_detector
        else:
            try:
                self.vision = VisionDetector()
                self.vision.load_model()
            except Exception as e:
                logging.error(f"Failed to initialize vision detector: {e}")
                self.vision = None
        
        # Detect screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        logging.info(f"Screen dimensions: {self.screen_width}x{self.screen_height}")
    
    def detect_chat_input(self, site_id: str = 'auto') -> Optional[Tuple[int, int]]:
        """
        Detect the chat input area using vision model
        
        Args:
            site_id: Site identifier for better accuracy ('qwen', 'perplexity', or 'auto')
            
        Returns:
            (x, y) coordinates of the chat input field or None if not found
        """
        if not self.vision:
            logging.error("Vision detector not available")
            return None
        
        logging.info(f"Detecting chat input area for site: {site_id}")
        
        # Elements to search for
        elements = []
        
        if site_id == 'auto' or site_id == 'qwen':
            elements.extend([
                "the chat input text area at the bottom of the screen",
                "the text entry field where users type messages to Qwen",
                "the message composition area at the bottom of the Qwen interface"
            ])
        
        if site_id == 'auto' or site_id == 'perplexity':
            elements.extend([
                "the chat input text box at the bottom of the screen",
                "the text field where users enter questions for Perplexity"
            ])
        
        # Generic elements to try if site-specific ones fail
        elements.extend([
            "the chat input area",
            "the text input box",
            "the area where you type messages",
            "the message input field at the bottom"
        ])
        
        # Take debug screenshot
        if self.debug:
            save_screenshot("detect_chat_input.png", directory="debug", compress=True)
            
        # Detect elements
        results = self.vision.detect_elements(elements)
        
        # Find the first detected input field
        for element, coords in results.items():
            if coords:
                logging.info(f"Detected chat input field at {coords} ({element})")
                return coords
        
        logging.warning("Failed to detect chat input field, using fallback coordinates")
        
        # Fallback: provide reasonable default coordinates based on screen size
        screen_width, screen_height = pyautogui.size()
        
        # Most chat interfaces have the input at bottom center
        fallback_x = screen_width // 2
        fallback_y = int(screen_height * 0.9)  # 90% down the screen
        
        logging.info(f"Using fallback chat input coordinates: ({fallback_x}, {fallback_y})")
        return (fallback_x, fallback_y)
    
    def detect_send_button(self, site_id: str = 'auto') -> Optional[Tuple[int, int]]:
        """
        Detect the send button using vision model
        
        Args:
            site_id: Site identifier for better accuracy ('qwen', 'perplexity', or 'auto')
            
        Returns:
            (x, y) coordinates of the send button or None if not found
        """
        if not self.vision:
            logging.error("Vision detector not available")
            return None
        
        logging.info(f"Detecting send button for site: {site_id}")
        
        # Elements to search for
        elements = []
        
        if site_id == 'auto' or site_id == 'qwen':
            elements.extend([
                "the send button next to the input area",
                "the paper airplane or arrow icon used to send messages"
            ])
        
        if site_id == 'auto' or site_id == 'perplexity':
            elements.extend([
                "the send arrow button",
                "the button to submit the question to Perplexity"
            ])
        
        # Generic elements to try if site-specific ones fail
        elements.extend([
            "the send button",
            "the submit button",
            "the arrow or paper airplane icon to send message"
        ])
        
        # Detect elements
        results = self.vision.detect_elements(elements)
        
        # Find the first detected send button
        for element, coords in results.items():
            if coords:
                logging.info(f"Detected send button at {coords} ({element})")
                return coords
        
        logging.warning("Failed to detect send button")
        return None
    
    def paste_text_to_chat(
        self, 
        text: str, 
        site_id: str = 'auto',
        use_keyboard_shortcut: bool = True
    ) -> bool:
        """
        Paste text to the detected chat input field and send it
        
        Args:
            text: Text to paste
            site_id: Site identifier ('qwen', 'perplexity', or 'auto')
            use_keyboard_shortcut: Whether to use keyboard shortcuts (Ctrl/Cmd+V) for pasting
            
        Returns:
            True if successful, False otherwise
        """
        if not text:
            logging.warning("No text provided to paste")
            return False
        
        # First detect the input field
        input_field = self.detect_chat_input(site_id)
        if not input_field:
            logging.error("Cannot paste text: chat input field not detected")
            return False
        
        # Then detect the send button
        send_button = self.detect_send_button(site_id)
        if not send_button:
            logging.warning("Send button not detected, will try using Enter key instead")
        
        # Copy text to clipboard
        logging.info(f"Copying text to clipboard: {text[:50]}...")
        pyperclip.copy(text)
        time.sleep(random.uniform(0.3, 0.7))
        
        # Click in the input field
        logging.info(f"Clicking input field at {input_field}")
        self.human.move_mouse(input_field[0], input_field[1])
        self.human.click()
        time.sleep(random.uniform(0.5, 1.0))
        
        # Optional: Select all existing text (if any)
        if random.random() < 0.7:  # Sometimes select all, sometimes just start typing
            logging.info("Selecting all existing text")
            if sys.platform == 'darwin':  # macOS
                self.human.hotkey('command', 'a')
            else:  # Windows/Linux
                self.human.hotkey('ctrl', 'a')
            time.sleep(random.uniform(0.3, 0.6))
        
        # Paste text
        logging.info("Pasting text")
        if use_keyboard_shortcut:
            # Use keyboard shortcut to paste
            if sys.platform == 'darwin':  # macOS
                self.human.hotkey('command', 'v')
            else:  # Windows/Linux
                self.human.hotkey('ctrl', 'v')
        else:
            # Right-click and select paste
            self.human.right_click()
            time.sleep(random.uniform(0.5, 0.8))
            
            # Usually "Paste" is the first or second option in the context menu
            paste_offset_y = random.randint(20, 30)
            current_x, current_y = pyautogui.position()
            self.human.move_mouse(current_x, current_y + paste_offset_y)
            self.human.click()
        
        # Take debug screenshot after pasting
        if self.debug:
            timestamp = int(time.time())
            save_screenshot(f"after_paste_{time.strftime('%Y%m%d-%H%M%S')}.png", directory="debug", compress=True)
        
        # Wait a bit after pasting
        time.sleep(random.uniform(0.5, 1.0))
        
        # Send the message
        logging.info("Sending message")
        if send_button:
            # Click the send button
            self.human.move_mouse(send_button[0], send_button[1])
            self.human.click()
        else:
            # Use Enter key if send button wasn't detected
            self.human.press_key('enter')
        
        # Take debug screenshot after sending
        if self.debug:
            timestamp = int(time.time())
            save_screenshot(f"after_send_{time.strftime('%Y%m%d-%H%M%S')}.png", directory="debug", compress=True)
        
        logging.info("Message sent successfully")
        return True

# Example usage
if __name__ == "__main__":
    # Create dependencies
    human = HumanInput()
    vision = VisionDetector()
    vision.load_model()
    
    # Create text paster with debug mode enabled
    paster = TextPaster(human, vision, debug=True)
    
    # Wait for user to position window
    print("Position your browser with the chat interface visible and press Enter...")
    input()
    
    # Try to paste a sample text
    sample_text = "What are the latest advancements in renewable energy technology? Please provide specific examples from the past year."
    
    success = paster.paste_text_to_chat(sample_text, site_id='auto')
    
    if success:
        print("Successfully pasted and sent the message!")
    else:
        print("Failed to paste and send the message.")
    
    # Clean up
    vision.unload_model()