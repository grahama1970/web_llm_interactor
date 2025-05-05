#!/usr/bin/env python3
"""
Proof of Concept: Chat Response Extraction with Qwen-VL

This script demonstrates the ability to extract text responses from AI chat interfaces
using Qwen-VL vision model. It captures a screenshot of the chat interface and uses
visual understanding to extract the AI's response text.

Usage:
  1. Open the target website with a visible AI response
  2. Run this script
  3. The script will attempt to extract the text response
  4. The extracted text will be saved to a file

Note: This script requires PyTorch, transformers, and the Qwen-VL model to be installed.
"""

import os
import sys
import time
import json
import argparse
import platform
import logging
from PIL import Image
import pyautogui

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Create debug and output directories
DEBUG_DIR = "debug"
OUTPUT_DIR = "responses"
os.makedirs(DEBUG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Chat Response Extraction Test")
    parser.add_argument("--timeout", type=int, default=5, 
                       help="Seconds to wait before starting (default: 5)")
    parser.add_argument("--model", type=str, default="Qwen/Qwen-VL-Chat",
                       help="Qwen-VL model to use (default: Qwen-VL-Chat)")
    parser.add_argument("--site", type=str, default="qwen",
                        choices=["qwen", "perplexity", "generic"],
                        help="Site type for response extraction optimization")
    parser.add_argument("--output-format", type=str, default="txt",
                        choices=["txt", "json", "md"],
                        help="Output format for extracted response")
    parser.add_argument("--include-query", action="store_true",
                        help="Try to extract the query as well as the response")
    return parser.parse_args()

def check_and_setup_device():
    """Check and setup the appropriate device (MPS, CUDA, or CPU)."""
    try:
        import torch
        
        # Check device availability
        device = None
        device_type = "cpu"  # Default fallback
        
        # Try to check for MPS, but handle potential attribute errors on older PyTorch
        has_mps = False
        try:
            has_mps = hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()
        except AttributeError:
            pass
            
        if has_mps:
            device_type = "mps"
            device = torch.device("mps")
            logging.info("Using MPS acceleration!")
            
        # Check for CUDA (NVIDIA GPUs)
        elif torch.cuda.is_available():
            device_type = "cuda"
            device = torch.device("cuda")
            logging.info("Using CUDA acceleration!")
            
        else:
            device = torch.device("cpu")
            logging.info("Using CPU (no GPU acceleration available)")
            
            # Provide additional info for Mac Intel users
            if platform.system() == 'Darwin' and platform.machine() == 'x86_64':
                logging.info("==================================================")
                logging.info("INFO: Intel Mac detected.")
                logging.info("You appear to be using PyTorch without MPS support.")
                logging.info("This is expected on Intel Macs with official PyTorch.")
                logging.info("==================================================")
        
        return device, device_type
    
    except ImportError:
        logging.error("PyTorch not installed. Please run the fix_torch.py script first.")
        sys.exit(1)

def load_vision_models(model_name, device):
    """Load Qwen-VL models with appropriate error handling."""
    try:
        from transformers import AutoProcessor, AutoModelForCausalLM
        
        logging.info(f"Loading Qwen-VL model: {model_name}")
        
        # Load model and processor
        model = AutoModelForCausalLM.from_pretrained(model_name)
        processor = AutoProcessor.from_pretrained(model_name)
        
        # Move model to device
        model = model.to(device)
        logging.info(f"Model loaded and moved to {device}")
        
        return model, processor
    
    except ImportError:
        logging.error("Transformers not installed. Install with: pip install transformers")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to load Qwen-VL model: {e}")
        sys.exit(1)

def capture_and_save_screenshot(prefix="response"):
    """Capture screenshot and save it."""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    screenshot = pyautogui.screenshot()
    filepath = os.path.join(DEBUG_DIR, f"{prefix}_{timestamp}.png")
    screenshot.save(filepath)
    logging.info(f"Saved {prefix} to {filepath}")
    return screenshot, filepath, timestamp

def get_site_specific_prompt(site_type, include_query=False):
    """Get site-specific prompt for better extraction results."""
    if site_type == "qwen":
        if include_query:
            return (
                "Extract the most recent chat conversation from this image of the Qwen.ai website. "
                "Include both the user query and the AI's response. Format as JSON with 'query' and 'response' fields. "
                "The query is usually shorter and at the top, while the response is typically longer and more detailed below. "
                "Only extract the most recent query and response pair, ignore older messages."
            )
        else:
            return (
                "Extract the most recent AI response text from this image of the Qwen.ai website. "
                "Look for the AI's response text which appears below the user's question. "
                "Do not include the user's query in your extraction. "
                "Include all text in the response, including any code blocks or lists."
            )
    elif site_type == "perplexity":
        if include_query:
            return (
                "Extract the most recent chat conversation from this image of the Perplexity.ai website. "
                "Include both the user query and the AI's response. Format as JSON with 'query' and 'response' fields. "
                "The query usually appears with a human icon, while the response typically has an AI icon. "
                "Only extract the most recent query and response pair, ignore older messages."
            )
        else:
            return (
                "Extract the most recent AI response text from this image of the Perplexity.ai website. "
                "Look for the AI's response text which appears with the Perplexity icon or in the assistant section. "
                "Do not include the user's query, citations, or controls. "
                "Include all text in the response including any lists, citations, or formatted content."
            )
    else:  # generic
        if include_query:
            return (
                "Extract the most recent chat conversation from this screenshot. "
                "Format your answer as JSON with 'query' and 'response' fields. "
                "The query is typically a short question or prompt, while the response is usually longer and more detailed. "
                "Only extract the most recent query and response pair, ignore earlier messages."
            )
        else:
            return (
                "Extract only the AI response text from this screenshot. "
                "The response typically appears after a user's query and is often longer, formatted, "
                "or contains detailed information. Ignore the user's question or prompt. "
                "Include all text in the response including any code blocks, lists, or citations."
            )

def extract_response(model, processor, device, site_type, screenshot=None, include_query=False):
    """Extract response text from chat interface using Qwen-VL."""
    logging.info("Extracting chat response text...")
    
    # Capture screenshot if not provided
    if screenshot is None:
        screenshot, _, _ = capture_and_save_screenshot()
    
    # Get appropriate prompt based on site type
    prompt = get_site_specific_prompt(site_type, include_query)
    
    try:
        # Process screenshot with vision model
        import torch
        inputs = processor(text=prompt, images=[screenshot], return_tensors="pt")
        
        # Move inputs to the correct device
        for key in inputs:
            if isinstance(inputs[key], torch.Tensor):
                inputs[key] = inputs[key].to(device)
        
        # Generate output
        outputs = model.generate(**inputs, max_new_tokens=1024)  # Increase token limit for long responses
        response = processor.decode(outputs[0], skip_special_tokens=True).strip()
        
        logging.info(f"Extracted text ({len(response)} chars)")
        
        # Process if JSON output is expected
        if include_query:
            try:
                # Check if the model already gave us JSON format
                json_data = json.loads(response)
                if 'query' in json_data and 'response' in json_data:
                    return json_data
            except json.JSONDecodeError:
                # If not JSON, do a simple split to extract query and response
                # This is very basic and might not work in all cases
                parts = response.split("\n\n", 1)
                if len(parts) > 1:
                    return {
                        "query": parts[0],
                        "response": parts[1]
                    }
                else:
                    return {
                        "query": "Could not extract query",
                        "response": response
                    }
        
        return response
        
    except Exception as e:
        logging.error(f"Error extracting response: {e}")
        return f"Error: {str(e)}"

def save_response(response, site_name, timestamp, output_format="txt", include_query=False):
    """Save extracted response to a file."""
    base_filename = f"{site_name}_{timestamp}"
    
    if output_format == "txt":
        # Plain text output
        filepath = os.path.join(OUTPUT_DIR, f"{base_filename}.txt")
        with open(filepath, 'w') as f:
            if include_query and isinstance(response, dict):
                f.write(f"Query:\n{response['query']}\n\n")
                f.write(f"Response:\n{response['response']}\n")
            else:
                f.write(str(response))
    
    elif output_format == "md":
        # Markdown output
        filepath = os.path.join(OUTPUT_DIR, f"{base_filename}.md")
        with open(filepath, 'w') as f:
            if include_query and isinstance(response, dict):
                f.write(f"# Query\n\n{response['query']}\n\n")
                f.write(f"# Response\n\n{response['response']}\n")
            else:
                f.write(f"# Extracted Response\n\n{response}\n")
    
    else:  # json
        # JSON output
        filepath = os.path.join(OUTPUT_DIR, f"{base_filename}.json")
        if include_query and isinstance(response, dict):
            data = {
                "query": response["query"],
                "response": response["response"],
                "site": site_name,
                "timestamp": timestamp
            }
        else:
            data = {
                "response": response,
                "site": site_name,
                "timestamp": timestamp
            }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    logging.info(f"Saved response to {filepath}")
    return filepath

def main():
    """Main function."""
    # Parse arguments
    args = parse_args()
    
    print("\n" + "=" * 60)
    print("Chat Response Extraction - Qwen-VL Proof of Concept")
    print("=" * 60)
    print(f"Site type: {args.site}")
    print(f"Output format: {args.output_format}")
    print(f"Include query: {args.include_query}")
    print("=" * 60 + "\n")
    
    # Setup
    device, device_type = check_and_setup_device()
    
    # This import is placed here to ensure it happens after device setup
    import torch
    
    # Load models
    model, processor = load_vision_models(args.model, device)
    
    # Wait for user to switch to correct window
    print(f"\nMake sure the target website with a visible response is on screen.")
    print(f"You have {args.timeout} seconds to switch to the browser window...")
    for i in range(args.timeout, 0, -1):
        print(f"{i}...", end=" ", flush=True)
        time.sleep(1)
    print("\n")
    
    try:
        # Capture screenshot
        screenshot, _, timestamp = capture_and_save_screenshot()
        
        # Extract response
        response = extract_response(
            model, 
            processor, 
            device, 
            args.site, 
            screenshot, 
            args.include_query
        )
        
        # Save response
        filepath = save_response(
            response, 
            args.site, 
            timestamp, 
            args.output_format, 
            args.include_query
        )
        
        # Display preview
        print("\n" + "=" * 60)
        print("EXTRACTION COMPLETE!")
        print(f"Response saved to: {filepath}")
        print("=" * 60 + "\n")
        
        if args.include_query and isinstance(response, dict):
            print("Query preview:")
            query_preview = response["query"][:100] + "..." if len(response["query"]) > 100 else response["query"]
            print(query_preview)
            print("\nResponse preview:")
            response_preview = response["response"][:200] + "..." if len(response["response"]) > 200 else response["response"]
            print(response_preview)
        else:
            print("Response preview:")
            preview = response[:300] + "..." if len(response) > 300 else response
            print(preview)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        logging.exception("Unhandled exception")
        print(f"\nError: {e}")
        
    print("\nDone!")
    return 0

if __name__ == "__main__":
    sys.exit(main())