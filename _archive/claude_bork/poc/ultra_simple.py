#!/usr/bin/env python3
"""
Ultra-simple script for LLM interaction via Chrome
No special JS, no f-strings, no complexity
"""

import subprocess
import time
import sys
import os

def ask_llm(question, wait_time=30):
    """
    Ask a question to the active Chrome tab
    This assumes Chrome is already open to an LLM chat page
    """
    # Escape the question for JS use
    safe_question = question.replace('"', '\\"').replace('\n', '\\n')
    
    # 1. Simple input and submit
    script = """
    tell application "Google Chrome"
        tell active tab of front window
            execute javascript "
                // Find input field
                var input = document.querySelector('textarea');
                if (!input) return 'No input field found';
                
                // Set value and focus
                input.focus();
                input.value = \\"%s\\";
                input.dispatchEvent(new Event('input', {bubbles: true}));
                
                // Click send button or press Enter
                var button = document.querySelector('button[type=\\"submit\\"]');
                if (button) {
                    button.click();
                } else {
                    input.dispatchEvent(new KeyboardEvent('keydown', {
                        key: 'Enter',
                        code: 'Enter',
                        keyCode: 13,
                        bubbles: true
                    }));
                }
                
                'Message sent'
            "
        end tell
    end tell
    """ % safe_question
    
    print(f"Sending: {question}")
    try:
        subprocess.run(["osascript", "-e", script], check=True)
        print("Message sent successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error sending message: {e}")
        return "Error: Failed to send message"
    
    # 2. Wait for response
    print(f"Waiting {wait_time} seconds...")
    time.sleep(wait_time)
    
    # 3. Get response
    capture = """
    tell application "Google Chrome"
        tell active tab of front window
            execute javascript "
                // Try common selectors for AI responses
                var selectors = [
                    '.markdown-content-container',
                    '.prose',
                    '.response',
                    '.chat-item-assistant',
                    '.ai-message'
                ];
                
                for (var i = 0; i < selectors.length; i++) {
                    var elements = document.querySelectorAll(selectors[i]);
                    if (elements && elements.length > 0) {
                        return elements[elements.length-1].innerText;
                    }
                }
                
                // Last resort - grab recent content
                document.body.scrollTop = document.body.scrollHeight;
                return document.body.innerText.substring(
                    Math.max(0, document.body.innerText.length - 3000)
                );
            "
        end tell
    end tell
    """
    
    print("Capturing response...")
    try:
        result = subprocess.run(["osascript", "-e", capture], 
                               capture_output=True, text=True, check=True)
        response = result.stdout.strip()
        
        # Save response to file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        os.makedirs("responses", exist_ok=True)
        filename = f"responses/simple_{timestamp}.txt"
        
        with open(filename, "w") as f:
            f.write(f"Question: {question}\n\n")
            f.write(f"Response:\n\n{response}")
        
        print(f"Saved to {filename}")
        return response
            
    except subprocess.CalledProcessError as e:
        print(f"Error capturing response: {e}")
        return "Error capturing response"

def main():
    if len(sys.argv) < 2:
        print("Usage: python ultra_simple.py 'Your question' [wait_time]")
        return 1
    
    question = sys.argv[1]
    wait_time = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    response = ask_llm(question, wait_time)
    
    print("\n--- Response ---")
    print(response[:500] + ("..." if len(response) > 500 else ""))
    print("-----------------")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())