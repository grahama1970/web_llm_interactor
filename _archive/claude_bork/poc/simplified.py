#!/usr/bin/env python3
"""
Ultra-simplified script for interacting with Qwen.ai through Chrome
Focuses on bare minimum necessary functionality to avoid syntax errors
"""

import subprocess
import time
import sys
import os
from pathlib import Path

# This script uses a minimal approach with no complex JavaScript

def escape_text(text):
    """Escape text for use in AppleScript and JavaScript."""
    return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

def send_message(question, url="https://chat.qwen.ai/"):
    """Send a message to the LLM using a very simple approach."""
    escaped_question = escape_text(question)
    
    script = f"""
    tell application "Google Chrome"
        activate
        set the URL of active tab of front window to "{url}"
        delay 2
        tell active tab of front window
            execute javascript "
                (function() {{
                    // Find the input field
                    const input = document.querySelector('textarea');
                    if (!input) return 'Input field not found';
                    
                    // Focus and set value
                    input.focus();
                    input.value = \\"{escaped_question}\\";
                    
                    // Trigger events
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    
                    // Find and click send button after a short delay
                    setTimeout(function() {{
                        const button = document.querySelector('button[type=\\"submit\\"]');
                        if (button) {{
                            button.click();
                            return 'Message sent via button';
                        }} else {{
                            const e = new KeyboardEvent('keydown', {{
                                key: 'Enter',
                                code: 'Enter',
                                keyCode: 13,
                                which: 13,
                                bubbles: true
                            }});
                            input.dispatchEvent(e);
                            return 'Message sent via Enter key';
                        }}
                    }}, 500);
                }})();
            "
        end tell
    end tell
    """
    
    try:
        print(f"Sending message: {question}")
        result = subprocess.run(['osascript', '-e', script], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        print("Message sent successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error sending message: {e.stderr}")
        return False

def capture_response(url="https://chat.qwen.ai/"):
    """Capture the response using a very simple approach."""
    script = f"""
    tell application "Google Chrome"
        activate
        tell active tab of front window
            execute javascript "
                (function() {{
                    // First look for response-specific elements
                    const responseElements = document.querySelectorAll('.markdown-content-container');
                    if (responseElements && responseElements.length > 0) {{
                        const lastResponse = responseElements[responseElements.length - 1];
                        return lastResponse.innerText || lastResponse.textContent;
                    }}
                    
                    // Fallback: get all assistant message content
                    const assistantMessages = document.querySelectorAll('.chat-item-assistant');
                    if (assistantMessages && assistantMessages.length > 0) {{
                        const lastMessage = assistantMessages[assistantMessages.length - 1];
                        return lastMessage.innerText || lastMessage.textContent;
                    }}
                    
                    // Last resort: capture all page text
                    return document.body.innerText;
                }})();
            "
        end tell
    end tell
    """
    
    try:
        print("Capturing response...")
        result = subprocess.run(['osascript', '-e', script], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        response_text = result.stdout.strip()
        print(f"Response captured ({len(response_text)} chars)")
        return response_text
    except subprocess.CalledProcessError as e:
        print(f"Error capturing response: {e.stderr}")
        return ""

def main():
    if len(sys.argv) < 2:
        print("Usage: python simplified.py 'Your question' [url] [wait_time]")
        sys.exit(1)
    
    # Get parameters
    question = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else "https://chat.qwen.ai/"
    wait_time = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    
    # Send message
    if not send_message(question, url):
        print("Failed to send message")
        sys.exit(1)
    
    # Wait for response
    print(f"Waiting {wait_time} seconds for response...")
    time.sleep(wait_time)
    
    # Capture response
    response = capture_response(url)
    
    # Save to file
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    os.makedirs("responses", exist_ok=True)
    with open(f"responses/response_{timestamp}.txt", "w") as f:
        f.write(f"Question: {question}\n\n")
        f.write(f"Response:\n\n{response}")
    
    # Display response
    print("\n--- Response ---")
    print(response[:1000] + ("..." if len(response) > 1000 else ""))
    print("-----------------")
    print(f"Full response saved to responses/response_{timestamp}.txt")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())