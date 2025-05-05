#!/usr/bin/env python3
"""
Simple working script for interacting with Qwen.ai and Perplexity.ai
"""

import subprocess
import time
import sys
import os

def ask_llm(question, wait_time=30, url="https://www.perplexity.ai/"):
    """Send a question to a web-based LLM and capture the response.
    
    Args:
        question: The question to ask
        wait_time: Time to wait for a response in seconds
        url: URL of the LLM site
        
    Returns:
        The response text
    """
    # Step 1: Navigate to the site and send the question
    escaped_question = question.replace("'", "\\'").replace('"', '\\"').replace("\n", "\\n")
    send_script = """
    tell application "Google Chrome"
        activate
        
        # Go to the correct URL
        set the URL of active tab of front window to "{0}"
        delay 3
        
        # Find and fill the input field
        tell active tab of front window
            execute javascript "
                const input = document.querySelector('textarea');
                if (input) {{
                    input.focus();
                    input.value = '{1}';
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    
                    setTimeout(() => {{
                        const button = document.querySelector('button[type=\\"submit\\"]') || 
                                       document.querySelector('button[aria-label=\\"Send message\\"]');
                        if (button) {{
                            button.click();
                        }} else {{
                            const e = new KeyboardEvent('keydown', {{
                                key: 'Enter',
                                code: 'Enter',
                                keyCode: 13,
                                bubbles: true
                            }});
                            input.dispatchEvent(e);
                        }}
                    }}, 300);
                }}
            "
        end tell
    end tell
    """.format(url, escaped_question)
    
    print(f"Sending question: {question}")
    subprocess.run(["osascript", "-e", send_script], capture_output=True)
    
    # Step 2: Wait for the response
    print(f"Waiting {wait_time} seconds for response...")
    time.sleep(wait_time)
    
    # Step 3: Capture the response
    capture_script = """
    tell application "Google Chrome"
        tell active tab of front window
            execute javascript "
                function getResponseText() {
                    // For Perplexity
                    if (window.location.href.includes('perplexity.ai')) {
                        const answers = document.querySelectorAll('.prose');
                        if (answers && answers.length > 0) {
                            return answers[answers.length - 1].innerText;
                        }
                    }
                    
                    // For Qwen
                    if (window.location.href.includes('qwen.ai')) {
                        const response = document.querySelector('#response-content-container');
                        if (response) {
                            return response.innerText;
                        }
                        
                        const markdown = document.querySelectorAll('.markdown-content-container');
                        if (markdown && markdown.length > 0) {
                            return markdown[markdown.length - 1].innerText;
                        }
                    }
                    
                    // Generic fallback - look for response class patterns
                    const selectors = [
                        '.assistant', '.chat-item-assistant', '.response',
                        '.bot-response', '.answer', '.ai-message'
                    ];
                    
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        if (elements && elements.length > 0) {
                            return elements[elements.length - 1].innerText;
                        }
                    }
                    
                    // Last resort - scroll to bottom and grab most recent text
                    window.scrollTo(0, document.body.scrollHeight);
                    return document.body.innerText.substring(document.body.innerText.length - 2000);
                }
                
                return getResponseText();
            "
        end tell
    end tell
    """
    
    print("Capturing response...")
    result = subprocess.run(["osascript", "-e", capture_script], capture_output=True, text=True)
    response = result.stdout.strip()
    
    # Save response to file
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    os.makedirs("responses", exist_ok=True)
    filename = f"responses/response_{timestamp}.txt"
    
    with open(filename, "w") as f:
        f.write(f"Question: {question}\n\n")
        f.write(f"Response:\n\n{response}")
    
    print(f"Response saved to {filename}")
    return response

def main():
    if len(sys.argv) < 2:
        print("Usage: python working.py 'Your question' [url] [wait_time]")
        return 1
    
    question = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else "https://www.perplexity.ai/"
    wait_time = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    
    response = ask_llm(question, wait_time, url)
    
    print("\n--- Response ---")
    # Print first 500 chars if response is longer than 500 chars
    if len(response) > 500:
        print(response[:500] + "...")
    else:
        print(response)
    print("-----------------")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())