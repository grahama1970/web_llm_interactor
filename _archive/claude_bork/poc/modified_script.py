#!/usr/bin/env python3
"""
Simplified version of applescript_spoof.py for Claude to use
"""

import subprocess
import time
import random
import sys
import json
from pathlib import Path
import re
import logging

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def escape_text(text):
    """Escape special characters for AppleScript."""
    return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

def get_chrome_url():
    """Get the URL of the active Chrome tab."""
    script = '''
    tell application "Google Chrome"
        get URL of active tab of front window
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get Chrome URL: {e.stderr}")
        return None

def send_message_to_browser(message):
    """
    Send a message to the current active tab in Chrome using simplified AppleScript.
    
    Args:
        message: Message text to send
    
    Returns:
        Success status and output message
    """
    escaped_message = escape_text(message)
    
    # Simple AppleScript that finds the textarea and injects text
    script = f'''
    tell application "Google Chrome"
        activate
        tell active tab of front window
            execute javascript "
                (function() {{
                    let inputField = document.querySelector('textarea') || 
                                    document.querySelector('div[contenteditable=\\"true\\"]');
                    if (!inputField) {{
                        return 'No input field found';
                    }}
                    
                    // Focus the input field
                    inputField.focus();
                    
                    // Set the value and trigger input events
                    if (inputField.tagName.toLowerCase() === 'textarea') {{
                        inputField.value = \\"{escaped_message}\\";
                    }} else {{
                        inputField.innerHTML = \\"{escaped_message}\\";
                    }}
                    
                    // Trigger input events
                    inputField.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    inputField.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    
                    // Find send button
                    let sendButton = document.querySelector('button[type=\\"submit\\"]') || 
                                    document.querySelector('button.send') ||
                                    document.querySelector('button:has(svg)');
                                    
                    if (sendButton) {{
                        // Click the send button
                        sendButton.click();
                        return 'Message sent via button click';
                    }} else {{
                        // Press Enter key if no button found
                        const enterEvent = new KeyboardEvent('keydown', {{
                            bubbles: true,
                            cancelable: true,
                            key: 'Enter',
                            code: 'Enter',
                            keyCode: 13
                        }});
                        inputField.dispatchEvent(enterEvent);
                        return 'Message sent via Enter key';
                    }}
                }})();
            "
        end tell
    end tell
    '''
    
    try:
        result = subprocess.run(['osascript', '-e', script], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        success_msg = result.stdout.strip()
        logger.info(f"Message sent successfully: {success_msg}")
        return True, success_msg
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to send message: {e.stderr}")
        return False, e.stderr

def capture_response():
    """
    Capture the response from the current active tab in Chrome.
    
    Returns:
        Response text or error message
    """
    # Improved JavaScript that extracts text from chat message elements with specific selectors for Qwen.ai
    script = '''
    tell application "Google Chrome"
        tell active tab of front window
            execute javascript "
                (function() {
                    // Qwen-specific selectors
                    if (window.location.href.includes('qwen.ai')) {
                        // For Qwen.ai - specifically target response content containers
                        const qwenResponseElements = document.querySelectorAll('.markdown-content-container');
                        if (qwenResponseElements && qwenResponseElements.length > 0) {
                            // Get the last response element
                            const responseElement = qwenResponseElements[qwenResponseElements.length - 1];
                            return responseElement.innerText || responseElement.textContent || 'No content found';
                        }
                    }
                    
                    // For Perplexity.ai
                    if (window.location.href.includes('perplexity.ai')) {
                        const perplexityResponses = document.querySelectorAll('.prose');
                        if (perplexityResponses && perplexityResponses.length > 0) {
                            const lastResponse = perplexityResponses[perplexityResponses.length - 1];
                            return lastResponse.innerText || lastResponse.textContent || 'No content found';
                        }
                    }
                    
                    // Generic approach for other platforms
                    const chatItems = document.querySelectorAll('.chat-item, .message, .chat-message, .message-container');
                    const assistantMessages = [];
                    
                    for (let i = 0; i < chatItems.length; i++) {
                        const el = chatItems[i];
                        const isUser = el.classList.contains('user-message') || 
                                       el.classList.contains('user') || 
                                       !!el.querySelector('.user');
                        
                        if (!isUser) {
                            assistantMessages.push(el.innerText || el.textContent || '');
                        }
                    }
                    
                    if (assistantMessages.length > 0) {
                        return assistantMessages[assistantMessages.length - 1];
                    }
                    
                    // Attempt to find response specifically in chat application layout
                    const responseContent = document.querySelector('#response-content-container, .response-content, .answer-content');
                    if (responseContent) {
                        return responseContent.innerText || responseContent.textContent || 'No content found';
                    }
                    
                    // Last resort: capture whole page content
                    return 'Could not find specific response element. First 500 chars of page content: ' + 
                           document.body.innerText.substring(0, 500) + '...';
                })();
            "
        end tell
    end tell
    '''
    
    try:
        result = subprocess.run(['osascript', '-e', script], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        response_text = result.stdout.strip()
        
        # Check if we got a meaningful response
        if response_text.startswith('Could not find specific response element') or len(response_text) < 10:
            logger.warning(f"Response may be incomplete: {response_text[:100]}...")
        else:
            logger.info(f"Successfully captured response ({len(response_text)} chars)")
            
        return response_text
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to capture response: {e.stderr}")
        return f"Error: {e.stderr}"

def ask_question(question, wait_time=30):
    """
    Main function to ask a question and get a response.
    
    Args:
        question: Question to ask
        wait_time: Time to wait for response in seconds (default: 30)
    
    Returns:
        Response text
    """
    # Get current URL for context
    current_url = get_chrome_url()
    if not current_url:
        return "Error: Could not determine current Chrome tab URL"
    
    logger.info(f"Current browser URL: {current_url}")
    logger.info(f"Sending question: '{question}'")
    
    # Send the question
    success, message = send_message_to_browser(question)
    if not success:
        return f"Failed to send message: {message}"
    
    # Wait for response
    logger.info(f"Waiting {wait_time} seconds for response...")
    time.sleep(wait_time)
    
    # Capture response
    response = capture_response()
    logger.info("Response captured")
    
    # Save response to file
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    safe_query = re.sub(r'[^a-zA-Z0-9]', '_', question[:30])
    filename = f"response_{timestamp}_{safe_query}.txt"
    
    Path("./responses").mkdir(parents=True, exist_ok=True)
    with open(f"./responses/{filename}", 'w') as f:
        f.write(f"Question: {question}\n\n")
        f.write(f"Response from {current_url} at {timestamp}:\n\n")
        f.write(response)
    
    logger.info(f"Response saved to ./responses/{filename}")
    return response

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python modified_script.py 'Your question here'")
        sys.exit(1)
    
    question = sys.argv[1]
    response = ask_question(question)
    
    print("\n--- Response ---")
    print(response)
    print("-----------------")