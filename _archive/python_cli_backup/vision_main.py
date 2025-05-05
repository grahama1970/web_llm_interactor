#!/usr/bin/env python3
"""
Main entry point for Vision-enhanced AI Chat Automation
"""

import os
import sys
import time
import json
import logging
import argparse
import random
from typing import List, Dict, Optional, Any, Tuple

# Import local modules
from src.browser import Browser, BrowserType
from src.human_input import HumanInput
from src.vision_detection import VisionDetector
from src.site_vision import create_vision_site_handler
from src.utils import save_screenshot, save_debug_info

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("vision_chat.log"),
        logging.StreamHandler()
    ]
)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Vision-enhanced AI Chat Automation")
    
    parser.add_argument(
        "--site", 
        choices=["qwen", "perplexity", "pplx"],
        default="qwen",
        help="AI chat site to use"
    )
    
    parser.add_argument(
        "--query", 
        type=str, 
        help="Query to send to the AI"
    )
    
    parser.add_argument(
        "--query-file", 
        type=str,
        help="File containing one query per line"
    )
    
    parser.add_argument(
        "--browser", 
        choices=["chrome", "firefox", "safari", "edge"],
        default="chrome",
        help="Browser to use for automation"
    )
    
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="responses",
        help="Directory to save responses"
    )
    
    parser.add_argument(
        "--output-format", 
        choices=["txt", "json", "md"],
        default="json",
        help="Output format for responses"
    )
    
    parser.add_argument(
        "--delay-min", 
        type=int, 
        default=10,
        help="Minimum delay between queries in seconds"
    )
    
    parser.add_argument(
        "--delay-max", 
        type=int, 
        default=30,
        help="Maximum delay between queries in seconds"
    )
    
    parser.add_argument(
        "--wait-for-login", 
        action="store_true",
        help="Wait for user to manually log in if needed"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug mode with extra logging and screenshots"
    )
    
    parser.add_argument(
        "--typing-speed", 
        type=int, 
        default=None,
        help="Typing speed in words per minute (default: random 40-100)"
    )
    
    parser.add_argument(
        "--no-vision", 
        action="store_true",
        help="Disable vision-based UI detection"
    )
    
    parser.add_argument(
        "--model", 
        type=str,
        default="Qwen/Qwen2.5-VL-7B",
        help="Vision-language model to use for UI detection"
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.query and not args.query_file:
        parser.error("Either --query or --query-file must be provided")
    
    if args.query_file and not os.path.exists(args.query_file):
        parser.error(f"Query file not found: {args.query_file}")
    
    return args

def read_queries_from_file(file_path: str) -> List[str]:
    """Read queries from a file, one per line"""
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def save_response(
    response: str,
    query: str,
    site_name: str,
    output_dir: str,
    output_format: str
) -> str:
    """Save a response to a file"""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create timestamp
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    
    # Base filename
    base_filename = f"{site_name}_{timestamp}"
    
    # Full path based on format
    if output_format == "txt":
        # Plain text output
        filepath = os.path.join(output_dir, f"{base_filename}.txt")
        with open(filepath, 'w') as f:
            f.write(f"Query: {query}\n\n")
            f.write(f"Response from {site_name} at {timestamp}:\n\n")
            f.write(response)
    
    elif output_format == "md":
        # Markdown output
        filepath = os.path.join(output_dir, f"{base_filename}.md")
        with open(filepath, 'w') as f:
            f.write(f"# Query\n\n{query}\n\n")
            f.write(f"# Response from {site_name}\n\n")
            f.write(f"*Timestamp: {timestamp}*\n\n")
            f.write(response)
    
    else:  # json
        # JSON output
        filepath = os.path.join(output_dir, f"{base_filename}.json")
        data = {
            "query": query,
            "response": response,
            "site": site_name,
            "timestamp": timestamp
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    logging.info(f"Saved response to {filepath}")
    return filepath

def run_automation(args) -> None:
    """Run the automation with the provided arguments"""
    # Set up dependencies
    browser = Browser(args.browser)
    human = HumanInput()
    
    # Initialize human inputs with provided parameters
    if args.typing_speed:
        human.typing_speed = args.typing_speed
    
    # Initialize vision detector if not disabled
    vision_detector = None
    if not args.no_vision:
        logging.info(f"Initializing vision detector with model {args.model}")
        vision_detector = VisionDetector(model_name=args.model)
        vision_detector.load_model()
    
    # Create site handler
    site = create_vision_site_handler(
        args.site, 
        browser, 
        human,
        vision_detector=vision_detector,
        use_vision=not args.no_vision,
        debug=args.debug
    )
    
    # Get all queries
    queries = []
    if args.query:
        queries.append(args.query)
    if args.query_file:
        queries.extend(read_queries_from_file(args.query_file))
    
    # Display startup info
    print("\n" + "="*60)
    print(f"Vision-enhanced AI Chat Automation - {args.site.upper()}")
    print(f"Using browser: {args.browser}")
    print(f"Vision detection: {'Enabled' if not args.no_vision else 'Disabled'}")
    print(f"Queries to process: {len(queries)}")
    print("="*60 + "\n")
    
    # Find existing browser or launch new one
    if not browser.find_process():
        print("Launching browser...")
        browser.launch_if_needed()
    else:
        print("Using existing browser process")
    
    # Navigate to site
    print(f"Navigating to {site.get_site_url()}...")
    site.navigate()
    
    # Wait for page to load
    time.sleep(3)
    
    # Take initial screenshot in debug mode
    if args.debug:
        save_screenshot("initial_screenshot.png", directory="debug")
    
    # Detect UI elements
    print("Detecting UI elements...")
    if site.detect_ui_elements():
        print("UI elements detected successfully")
    else:
        print("Failed to detect some UI elements - may affect automation")
    
    # Check login status
    if not site.is_logged_in():
        if args.wait_for_login:
            print("\nNot logged in. Please log in manually.")
            input("Press Enter when you've completed the login process...")
            
            # Detect UI elements again after login
            site.detect_ui_elements(force_refresh=True)
        else:
            print("\nWARNING: Not logged in. Responses may be limited.")
    else:
        print("Login detected - proceeding with queries")
    
    # Process each query
    for i, query in enumerate(queries):
        print(f"\nProcessing query {i+1}/{len(queries)}: {query[:50]}...")
        
        # Check for CAPTCHA before sending
        if site.detect_captcha():
            print("\nCAPTCHA detected - waiting for manual solution")
            if not site.wait_for_captcha_solution():
                print("CAPTCHA solution timed out, skipping query")
                continue
        
        # Send the query
        print("Sending query...")
        if site.send_message(query):
            # Wait for and get response
            print("Waiting for response...")
            response = site.get_response()
            
            # Save the response
            print("Saving response...")
            save_response(
                response, 
                query, 
                args.site, 
                args.output_dir, 
                args.output_format
            )
            
            # Print a preview
            preview = response[:200] + "..." if len(response) > 200 else response
            print(f"\nResponse preview:\n{preview}")
        else:
            print("Failed to send query")
        
        # Add delay between queries
        if i < len(queries) - 1:
            delay = random.randint(args.delay_min, args.delay_max)
            print(f"\nWaiting {delay} seconds before next query...")
            time.sleep(delay)
    
    print("\nAll queries processed!")
    
    # Clean up
    if vision_detector:
        vision_detector.unload_model()

if __name__ == "__main__":
    try:
        args = parse_args()
        run_automation(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        logging.exception("Unhandled exception")
        print(f"\nError: {e}")
    finally:
        print("\nAutomation complete.")