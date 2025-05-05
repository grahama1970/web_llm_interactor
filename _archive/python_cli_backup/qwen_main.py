#!/usr/bin/env python3
"""
Main entry point for Qwen-VL enhanced chat automation using vision-based UI detection.

This script uses Qwen-VL to identify the chat input field's pixel dimensions and PyAutoGUI
to simulate mouse clicks and text pasting, bypassing browser automation tools to avoid
Qwen's anti-bot measures.
"""

import os
import sys
import time
import json
import logging
import argparse
import random
from typing import List, Dict, Optional, Tuple
from PIL import Image
import pyautogui
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

# Configure PyAutoGUI
pyautogui.FAILSAFE = True  # Move mouse to top-left to abort
pyautogui.PAUSE = 0.5  # Small pause between actions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("qwen_chat.log"), logging.StreamHandler()],
)


class UIChatAutomation:
    """Handles vision-based UI automation using Qwen-VL and PyAutoGUI."""

    def __init__(self, site_name: str, use_vision: bool, debug: bool, qwen_model: str):
        self.site_name = site_name
        self.use_vision = use_vision
        self.debug = debug
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(qwen_model)
        self.processor = AutoProcessor.from_pretrained(qwen_model)
        self.screenshot_dir = "screenshots" if debug else None
        if debug:
            os.makedirs(self.screenshot_dir, exist_ok=True)

    def initialize(self) -> bool:
        """Ensure Qwen-VL is loaded and screen is ready."""
        logging.info("Initializing Qwen-VL model...")
        try:
            # Verify model is accessible
            test_prompt = "Describe this image."
            test_image = Image.new("RGB", (100, 100))  # Dummy image for test
            inputs = self.processor(
                text=test_prompt, images=[test_image], return_tensors="pt"
            )
            self.model.generate(**inputs)
            logging.info("Qwen-VL model initialized successfully.")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize Qwen-VL: {e}")
            return False

    def capture_screenshot(self) -> Image.Image:
        """Capture a screenshot of the entire screen."""
        screenshot = pyautogui.screenshot()
        image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        if self.debug:
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            filepath = os.path.join(self.screenshot_dir, f"screenshot_{timestamp}.png")
            image.save(filepath)
            logging.info(f"Saved screenshot to {filepath}")
        return image

    def detect_chat_input(self) -> Optional[Dict]:
        """Use Qwen-VL to detect chat input field's bounding box."""
        screenshot = self.capture_screenshot()
        prompt = (
            "Identify the chat input field (textarea or text box where users type messages) "
            "in the screenshot. Return the bounding box coordinates as JSON with "
            "{'top_left': [x, y], 'bottom_right': [x, y]}."
        )
        try:
            inputs = self.processor(
                text=prompt, images=[screenshot], return_tensors="pt"
            )
            outputs = self.model.generate(**inputs)
            response = self.processor.decode(outputs[0], skip_special_tokens=True)
            bbox = json.loads(response)
            if "top_left" in bbox and "bottom_right" in bbox:
                x1, y1 = bbox["top_left"]
                x2, y2 = bbox["bottom_right"]
                width = x2 - x1
                height = y2 - y1
                logging.info(
                    f"Chat input detected: {width}x{height} pixels at ({x1}, {y1}) to ({x2}, {y2})"
                )
                return {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "width": width,
                    "height": height,
                }
            else:
                logging.error("Invalid bounding box format from Qwen-VL")
                return None
        except Exception as e:
            logging.error(f"Failed to detect chat input: {e}")
            return None

    def detect_captcha(self) -> bool:
        """Use Qwen-VL to check for CAPTCHA presence."""
        screenshot = self.capture_screenshot()
        prompt = "Is there a CAPTCHA (e.g., 'Select all images with cars') visible in the screenshot? Answer 'Yes' or 'No'."
        try:
            inputs = self.processor(
                text=prompt, images=[screenshot], return_tensors="pt"
            )
            outputs = self.model.generate(**inputs)
            response = self.processor.decode(
                outputs[0], skip_special_tokens=True
            ).strip()
            is_captcha = response.lower() == "yes"
            if is_captcha:
                logging.warning("CAPTCHA detected")
            return is_captcha
        except Exception as e:
            logging.error(f"Failed to detect CAPTCHA: {e}")
            return False

    def wait_for_captcha_solution(self, timeout: int = 60) -> bool:
        """Wait for CAPTCHA to be resolved manually."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.detect_captcha():
                logging.info("CAPTCHA resolved")
                return True
            time.sleep(5)
        logging.error("CAPTCHA solution timed out")
        return False

    def send_message(self, query: str) -> bool:
        """Click into chat input and paste query using PyAutoGUI."""
        bbox = self.detect_chat_input()
        if not bbox:
            logging.error("Cannot send message: Chat input not found")
            return False

        try:
            # Calculate center of chat input
            center_x = bbox["x1"] + bbox["width"] // 2
            center_y = bbox["y1"] + bbox["height"] // 2

            # Move mouse to center with human-like movement
            pyautogui.moveTo(
                center_x, center_y, duration=0.5, tween=pyautogui.easeInOutQuad
            )
            pyautogui.click()

            # Paste query and submit
            pyautogui.write(query)
            pyautogui.press("enter")

            logging.info(f"Sent query: {query[:50]}...")
            return True
        except Exception as e:
            logging.error(f"Failed to send message: {e}")
            return False

    def get_response(self, query: str) -> str:
        """Extract response using Qwen-VL (placeholder implementation)."""
        # Note: This is a simplified version. In a full implementation, Qwen-VL would
        # analyze a screenshot to extract the response text from the chat area.
        time.sleep(5)  # Wait for response to appear
        screenshot = self.capture_screenshot()
        prompt = "Extract the latest response text from the chat conversation in the screenshot."
        try:
            inputs = self.processor(
                text=prompt, images=[screenshot], return_tensors="pt"
            )
            outputs = self.model.generate(**inputs)
            response = self.processor.decode(outputs[0], skip_special_tokens=True)
            logging.info(f"Extracted response: {response[:50]}...")
            return response
        except Exception as e:
            logging.error(f"Failed to extract response: {e}")
            return "Error: Could not extract response"

    def check_login_status(self, wait_for_login: bool) -> bool:
        """Check if logged in using Qwen-VL."""
        screenshot = self.capture_screenshot()
        prompt = "Is there a login button or sign-in prompt visible in the screenshot? Answer 'Yes' or 'No'."
        try:
            inputs = self.processor(
                text=prompt, images=[screenshot], return_tensors="pt"
            )
            outputs = self.model.generate(**inputs)
            response = self.processor.decode(
                outputs[0], skip_special_tokens=True
            ).strip()
            is_logged_in = response.lower() == "no"
            if not is_logged_in and wait_for_login:
                logging.info("Waiting for manual login...")
                time.sleep(30)  # Give user time to log in
                return self.check_login_status(False)
            return is_logged_in
        except Exception as e:
            logging.error(f"Failed to check login status: {e}")
            return False

    def cleanup(self):
        """Clean up resources."""
        logging.info("Cleaning up...")
        # No browser to close, as we use PyAutoGUI


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Qwen-VL Enhanced Chat Automation")
    parser.add_argument(
        "--site",
        choices=["qwen"],
        default="qwen",
        help="AI chat site to use (only Qwen supported)",
    )
    parser.add_argument("--query", type=str, help="Query to send to the AI")
    parser.add_argument(
        "--query-file", type=str, help="File containing one query per line"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="responses",
        help="Directory to save responses",
    )
    parser.add_argument(
        "--output-format",
        choices=["txt", "json", "md"],
        default="json",
        help="Output format for responses",
    )
    parser.add_argument(
        "--delay-min",
        type=int,
        default=10,
        help="Minimum delay between queries in seconds",
    )
    parser.add_argument(
        "--delay-max",
        type=int,
        default=30,
        help="Maximum delay between queries in seconds",
    )
    parser.add_argument(
        "--wait-for-login",
        action="store_true",
        help="Wait for user to manually log in if needed",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with extra logging and screenshots",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="Qwen/Qwen2.5-VL-3B-Instruct",
        help="Vision model to use for UI detection",
    )
    args = parser.parse_args()

    if not args.query and not args.query_file:
        parser.error("Either --query or --query-file must be provided")
    if args.query_file and not os.path.exists(args.query_file):
        parser.error(f"Query file not found: {args.query_file}")

    return args


def read_queries_from_file(file_path: str) -> List[str]:
    """Read queries from a file, one per line."""
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def save_response(
    response: str, query: str, site_name: str, output_dir: str, output_format: str
) -> str:
    """Save a response to a file."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    base_filename = f"{site_name}_{timestamp}"

    if output_format == "txt":
        filepath = os.path.join(output_dir, f"{base_filename}.txt")
        with open(filepath, "w") as f:
            f.write(f"Query: {query}\n\n")
            f.write(f"Response from {site_name} at {timestamp}:\n\n")
            f.write(response)
    elif output_format == "md":
        filepath = os.path.join(output_dir, f"{base_filename}.md")
        with open(filepath, "w") as f:
            f.write(f"# Query\n\n{query}\n\n")
            f.write(f"# Response from {site_name}\n\n")
            f.write(f"*Timestamp: {timestamp}*\n\n")
            f.write(response)
    else:  # json
        filepath = os.path.join(output_dir, f"{base_filename}.json")
        data = {
            "query": query,
            "response": response,
            "site": site_name,
            "timestamp": timestamp,
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    logging.info(f"Saved response to {filepath}")
    return filepath


def main():
    """Main entry point."""
    args = parse_args()

    queries = []
    if args.query:
        queries.append(args.query)
    if args.query_file:
        queries.extend(read_queries_from_file(args.query_file))

    print("\n" + "=" * 60)
    print(f"Qwen-VL Enhanced Chat Automation - {args.site.upper()}")
    print(f"Using vision-based detection with {args.model}")
    print(f"Queries to process: {len(queries)}")
    print("=" * 60 + "\n")

    try:
        automation = UIChatAutomation(
            site_name=args.site,
            use_vision=True,  # Vision is always enabled
            debug=args.debug,
            qwen_model=args.model,
        )

        print("Initializing automation...")
        if not automation.initialize():
            print("Initialization failed. Exiting.")
            return 1

        print("Checking login status...")
        if not automation.check_login_status(wait_for_login=args.wait_for_login):
            print("Not logged in. Proceeding anyway, but results may be limited.")
        else:
            print("Login detected.")

        for i, query in enumerate(queries):
            print(
                f"\nProcessing query {i + 1}/{len(queries)}: {query[:50]}..."
                if len(query) > 50
                else f"\nProcessing query {i + 1}/{len(queries)}: {query}"
            )

            if automation.detect_captcha():
                print("\nCAPTCHA detected - waiting for manual solution")
                if not automation.wait_for_captcha_solution():
                    print("CAPTCHA solution timed out, skipping query")
                    continue

            print("Sending query...")
            if automation.send_message(query):
                print("Waiting for response...")
                response = automation.get_response(query)

                print("Saving response...")
                save_response(
                    response, query, args.site, args.output_dir, args.output_format
                )

                preview = response[:200] + "..." if len(response) > 200 else response
                print(f"\nResponse preview:\n{preview}")
            else:
                print("Failed to send query")

            if i < len(queries) - 1:
                delay = random.randint(args.delay_min, args.delay_max)
                print(f"\nWaiting {delay} seconds before next query...")
                time.sleep(delay)

        print("\nAll queries processed!")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        logging.exception("Unhandled exception")
        print(f"\nError: {e}")
    finally:
        if "automation" in locals():
            automation.cleanup()
        print("\nAutomation complete.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
