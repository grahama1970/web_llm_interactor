#!/usr/bin/env python3
"""
Interface script for Claude to communicate with web-based LLMs via Chrome
"""

import subprocess
import time
import sys
import json
import re
from pathlib import Path
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("claude_interface.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Pre-defined LLM URLs 
LLM_URLS = {
    "perplexity": "https://www.perplexity.ai/",
    "qwen": "https://chat.qwen.ai/",
    "claude": "https://claude.ai/chat",
    "llama": "https://www.llama.fi/"
}

def escape_text(text):
    """Escape special characters for AppleScript and JavaScript."""
    return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

def send_message_to_browser(message, max_retries=2):
    """
    Send a message to the current active tab in Chrome.
    
    Args:
        message: Message text to send
        max_retries: Number of retry attempts
    
    Returns:
        Success status and output message
    """
    escaped_message = escape_text(message)
    
    # JavaScript for finding and interacting with input field
    script = f'''
    tell application "Google Chrome"
        activate
        tell active tab of front window
            execute javascript "
                (function() {{
                    // Find input field with retry logic
                    function findInputField() {{
                        return document.querySelector('textarea') || 
                               document.querySelector('div[contenteditable=\\"true\\"]') ||
                               document.querySelector('.input');
                    }}
                    
                    let inputField = findInputField();
                    if (!inputField) {{
                        // Wait and retry if not found immediately
                        return new Promise(resolve => {{
                            setTimeout(() => {{
                                inputField = findInputField();
                                if (!inputField) {{
                                    resolve('No input field found after retry');
                                    return;
                                }}
                                setupAndSend(inputField).then(result => resolve(result));
                            }}, 1000);
                        }});
                    }}
                    
                    function setupAndSend(inputField) {{
                        return new Promise(resolve => {{
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
                            
                            // Find send button with retry logic
                            function findSendButton() {{
                                return document.querySelector('button[type=\\"submit\\"]') || 
                                       document.querySelector('button.send') ||
                                       document.querySelector('button:has(svg)') ||
                                       document.querySelector('[aria-label=\\"Send message\\"]');
                            }}
                            
                            let sendButton = findSendButton();
                            
                            if (sendButton) {{
                                // Click the send button
                                sendButton.click();
                                resolve('Message sent via button click');
                            }} else {{
                                // Try Enter key if no button found
                                const enterEvent = new KeyboardEvent('keydown', {{
                                    bubbles: true,
                                    cancelable: true,
                                    key: 'Enter',
                                    code: 'Enter',
                                    keyCode: 13
                                }});
                                inputField.dispatchEvent(enterEvent);
                                resolve('Message sent via Enter key');
                            }}
                        }});
                    }}
                    
                    return setupAndSend(inputField);
                }})();
            "
        end tell
    end tell
    '''
    
    # Try multiple times if failed
    for attempt in range(max_retries + 1):
        try:
            result = subprocess.run(['osascript', '-e', script], 
                                   capture_output=True, 
                                   text=True, 
                                   check=True)
            success_msg = result.stdout.strip()
            logger.info(f"Message sent successfully: {success_msg}")
            return True, success_msg
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to send message (attempt {attempt+1}): {e.stderr}")
            if attempt < max_retries:
                logger.info(f"Retrying in 2 seconds...")
                time.sleep(2)
            else:
                return False, e.stderr

def capture_response(max_wait_time=45, polling_interval=5, max_retries=3):
    """
    Capture the response from the current active tab in Chrome.
    Uses polling to wait for response to complete.
    
    Args:
        max_wait_time: Maximum time to wait for response in seconds
        polling_interval: Time between checks in seconds
        max_retries: Number of retry attempts
        
    Returns:
        Response text or error message
    """
    # JavaScript for detecting and capturing response
    script = '''
    tell application "Google Chrome"
        tell active tab of front window
            execute javascript "
                (function() {
                    // Extract current URL
                    const currentUrl = window.location.href;
                    
                    // Platform-specific selectors
                    if (currentUrl.includes('qwen.ai')) {
                        // Qwen.ai specific selectors (try multiple patterns)
                        
                        // Try markdown content first
                        const qwenResponses = document.querySelectorAll('.markdown-content-container');
                        if (qwenResponses && qwenResponses.length > 0) {
                            const lastResponse = qwenResponses[qwenResponses.length - 1];
                            const content = lastResponse.innerText || lastResponse.textContent;
                            if (content && content.length > 20) {
                                return content;
                            }
                        }
                        
                        // Try message container
                        const messageContainers = document.querySelectorAll('.chat-item-assistant');
                        if (messageContainers && messageContainers.length > 0) {
                            const lastMessage = messageContainers[messageContainers.length - 1];
                            return lastMessage.innerText || lastMessage.textContent;
                        }
                        
                        // Try response panel
                        const responsePanel = document.querySelector('#response-content-container');
                        if (responsePanel) {
                            return responsePanel.innerText || responsePanel.textContent;
                        }
                    }
                    
                    if (currentUrl.includes('perplexity.ai')) {
                        // Perplexity.ai specific selectors
                        const perplexityResponses = document.querySelectorAll('.prose');
                        if (perplexityResponses && perplexityResponses.length > 0) {
                            const lastResponse = perplexityResponses[perplexityResponses.length - 1];
                            return lastResponse.innerText || lastResponse.textContent;
                        }
                    }
                    
                    // Generic approach for other platforms
                    // Look for the most common container patterns
                    const containers = [
                        // General chat UI patterns
                        '.message-content:not(.user)',
                        '.chat-message:not(.user)',
                        '.chat-item:not(.user)',
                        '.response-content',
                        '.assistant-message',
                        '.ai-response',
                        
                        // Specific known platform selectors
                        '.markdown-content-container',
                        '#response-content-container',
                        '.prose',
                        '.message-body'
                    ];
                    
                    // Try each selector pattern
                    for (const selector of containers) {
                        const elements = document.querySelectorAll(selector);
                        if (elements && elements.length > 0) {
                            const lastElement = elements[elements.length - 1];
                            const content = lastElement.innerText || lastElement.textContent;
                            if (content && content.trim().length > 20) {
                                return content;
                            }
                        }
                    }
                    
                    // If no specific container found, try to determine if response is still generating
                    const loadingIndicators = document.querySelectorAll('.thinking, .loading, .generating, .spinner');
                    if (loadingIndicators && loadingIndicators.length > 0) {
                        return '__STILL_GENERATING__';
                    }
                    
                    // Last resort: return representative sample of page content
                    return 'FALLBACK_CAPTURE: ' + document.body.innerText.substring(0, 1000);
                })();
            "
        end tell
    end tell
    '''
    
    start_time = time.time()
    last_content = None
    last_content_time = None
    content_stable_duration = 0  # How long has content remained the same
    
    # Poll until response is complete or timeout
    while time.time() - start_time < max_wait_time:
        try:
            for retry in range(max_retries):
                try:
                    result = subprocess.run(['osascript', '-e', script], 
                                          capture_output=True, 
                                          text=True, 
                                          check=True)
                    response_text = result.stdout.strip()
                    break
                except Exception as e:
                    if retry == max_retries - 1:
                        raise e
                    time.sleep(1)
            
            # Check if still generating
            if response_text == '__STILL_GENERATING__':
                logger.info("Response still generating...")
                time.sleep(polling_interval)
                continue
                
            # Compare with previous content
            if response_text == last_content:
                # Content is stable
                if last_content_time is None:
                    last_content_time = time.time()
                
                # Check if content has been stable for required duration
                content_stable_duration = time.time() - last_content_time
                if content_stable_duration >= 5 and len(response_text) > 50:  # 5 seconds of stability
                    logger.info(f"Response appears complete and stable for {content_stable_duration:.1f} seconds")
                    return response_text
            else:
                # Content changed, reset stability timer
                last_content = response_text
                last_content_time = time.time()
                logger.info(f"Response updated, length: {len(response_text)} chars")
            
            # Wait before next check
            time.sleep(polling_interval)
            
        except Exception as e:
            logger.error(f"Error capturing response: {str(e)}")
            time.sleep(polling_interval)
    
    # If we get here, return whatever we have (timeout reached)
    if last_content and len(last_content) > 20:
        logger.warning(f"Maximum wait time reached, returning content of {len(last_content)} chars")
        return last_content
    
    return "Error: Failed to capture a complete response within the time limit"

def navigate_to_url(url):
    """
    Navigate Chrome to a specific URL.
    
    Args:
        url: URL to navigate to
        
    Returns:
        Success status
    """
    # First try to navigate to an existing tab if it exists
    find_tab_script = f'''
    tell application "Google Chrome"
        activate
        set foundTab to false
        set targetURL to "{url}"
        
        repeat with w in windows
            set tabIndex to 1
            repeat with t in tabs of w
                if URL of t contains targetURL then
                    set active tab index of w to tabIndex
                    set index of w to 1
                    set foundTab to true
                    exit repeat
                end if
                set tabIndex to tabIndex + 1
            end repeat
            if foundTab then exit repeat
        end repeat
        
        return foundTab
    end tell
    '''
    
    try:
        # First try to find an existing tab
        result = subprocess.run(['osascript', '-e', find_tab_script],
                              capture_output=True,
                              text=True,
                              check=True)
        
        found_tab = result.stdout.strip().lower() == "true"
        
        if found_tab:
            logger.info(f"Found and activated existing tab for {url}")
            return True
            
        # If no existing tab, create a new one
        new_tab_script = f'''
        tell application "Google Chrome"
            activate
            if (count of windows) is 0 then
                make new window
            else
                tell front window
                    make new tab with properties {{URL:"{url}"}}
                end tell
            end if
        end tell
        '''
        
        subprocess.run(['osascript', '-e', new_tab_script], 
                      capture_output=True, 
                      text=True, 
                      check=True)
        
        logger.info(f"Opened new tab and navigated to {url}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to navigate: {e.stderr}")
        
        # Last resort - direct navigation
        try:
            direct_script = f'''
            tell application "Google Chrome"
                activate
                set URL of active tab of front window to "{url}"
            end tell
            '''
            
            subprocess.run(['osascript', '-e', direct_script], 
                          capture_output=True, 
                          text=True, 
                          check=True)
                          
            logger.info(f"Navigated directly to {url}")
            return True
            
        except subprocess.CalledProcessError as e2:
            logger.error(f"All navigation attempts failed: {e2.stderr}")
            return False

def get_current_url():
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
        logger.error(f"Failed to get current URL: {e.stderr}")
        return None

def ask_llm(question, llm="qwen", wait_time=45, retries=2, save_response=True):
    """
    Main function to ask a question to a web-based LLM.
    
    Args:
        question: Question to ask
        llm: LLM to use (perplexity, qwen, etc.)
        wait_time: Maximum time to wait for response
        retries: Number of retry attempts
        save_response: Whether to save the response to a file
        
    Returns:
        Response text, or error message
    """
    # Get LLM URL
    url = LLM_URLS.get(llm.lower())
    if not url:
        if llm.startswith(('http://', 'https://')):
            url = llm  # Use provided URL directly
        else:
            return f"Error: Unknown LLM '{llm}'. Available options: {', '.join(LLM_URLS.keys())}"
    
    # Check if already on the correct site, otherwise navigate
    current_url = get_current_url()
    if not current_url or not current_url.startswith(url):
        logger.info(f"Navigating to {url}")
        if not navigate_to_url(url):
            return f"Error: Failed to navigate to {url}"
        time.sleep(3)  # Wait for page to load
    
    # Send the question
    for attempt in range(retries + 1):
        success, message = send_message_to_browser(question)
        if success:
            break
        elif attempt < retries:
            logger.info(f"Retrying message send (attempt {attempt+1}/{retries+1})...")
            time.sleep(2)
        else:
            return f"Error: Failed to send message after {retries+1} attempts"
    
    # Wait for and capture the response
    logger.info(f"Waiting up to {wait_time} seconds for response...")
    response = capture_response(max_wait_time=wait_time)
    
    # Check if response is valid/complete
    if not response or len(response) < 20 or response.startswith("Error:"):
        return f"Error capturing response: {response}"
    
    # Clean up response
    response = response.strip()
    
    # Save response if requested
    if save_response:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        safe_query = re.sub(r'[^a-zA-Z0-9]', '_', question[:30])
        filename = f"{llm}_{timestamp}_{safe_query}.txt"
        
        Path("./responses").mkdir(parents=True, exist_ok=True)
        with open(f"./responses/{filename}", 'w') as f:
            f.write(f"Question: {question}\n\n")
            f.write(f"Response from {llm.upper()} at {timestamp}:\n\n")
            f.write(response)
        
        logger.info(f"Response saved to ./responses/{filename}")
    
    return response

def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(description="Claude interface for web-based LLMs")
    parser.add_argument("question", help="Question to ask the LLM")
    parser.add_argument("--llm", default="qwen", help="LLM to use (perplexity, qwen, or URL)")
    parser.add_argument("--wait", type=int, default=45, help="Max wait time in seconds")
    parser.add_argument("--no-save", action="store_true", help="Don't save response to file")
    parser.add_argument("--retries", type=int, default=2, help="Number of retry attempts")
    
    args = parser.parse_args()
    
    try:
        response = ask_llm(
            args.question, 
            llm=args.llm, 
            wait_time=args.wait, 
            retries=args.retries,
            save_response=not args.no_save
        )
        
        # Output only the response (for easier parsing by Claude)
        print(response)
        
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}")
        print(f"ERROR: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())