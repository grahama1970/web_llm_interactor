#!/usr/bin/env python3
"""
Minimal fixed version of the original applescript_spoof.py
"""

import subprocess
import time
import random
import sys
import json
from pathlib import Path
import re
from loguru import logger

# Configure Loguru logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

def escape_for_applescript(text):
    """Escape special characters for AppleScript and JavaScript compatibility."""
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

def build_advanced_mouse_simulation():
    """Generate advanced JavaScript for human-like mouse movement to avoid bot detection."""
    return """
        // Advanced function to create a natural Bezier curve with random deviations
        function createNaturalBezierCurve(startX, startY, endX, endY) {
            const numControlPoints = Math.floor(Math.random() * 4) + 2; // 2-5 control points
            const controlPoints = [];
            const totalDistance = Math.sqrt(Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2));
            for (let i = 0; i < numControlPoints; i++) {
                const t = (i + 1) / (numControlPoints + 1);
                const midX = startX + t * (endX - startX);
                const midY = startY + t * (endY - startY);
                const maxDeviation = totalDistance * (0.2 + Math.random() * 0.3); // 20-50% deviation
                const deviation = Math.random() * maxDeviation - maxDeviation / 2;
                const angle = Math.random() * 2 * Math.PI;
                controlPoints.push({
                    x: midX + deviation * Math.cos(angle),
                    y: midY + deviation * Math.sin(angle)
                });
            }
            return { start: { x: startX, y: startY }, end: { x: endX, y: endY }, controlPoints: controlPoints };
        }

        // Calculate a point on a Bezier curve at time t (0-1)
        function getPointOnBezierCurve(curve, t) {
            const { start, end, controlPoints } = curve;
            if (controlPoints.length === 1) {
                const cp = controlPoints[0];
                const x = Math.pow(1 - t, 2) * start.x + 2 * (1 - t) * t * cp.x + Math.pow(t, 2) * end.x;
                const y = Math.pow(1 - t, 2) * start.y + 2 * (1 - t) * t * cp.y + Math.pow(t, 2) * end.y;
                return { x, y };
            } else if (controlPoints.length === 2) {
                const cp1 = controlPoints[0];
                const cp2 = controlPoints[1];
                const x = Math.pow(1 - t, 3) * start.x + 3 * Math.pow(1 - t, 2) * t * cp1.x + 3 * (1 - t) * Math.pow(t, 2) * cp2.x + Math.pow(t, 3) * end.x;
                const y = Math.pow(1 - t, 3) * start.y + 3 * Math.pow(1 - t, 2) * t * cp1.y + 3 * (1 - t) * Math.pow(t, 2) * cp2.y + Math.pow(t, 3) * end.y;
                return { x, y };
            } else {
                const points = [start, ...controlPoints, end];
                let currentPoints = [...points];
                for (let k = points.length - 1; k > 0; k--) {
                    const newPoints = [];
                    for (let i = 0; i < k; i++) {
                        const x = (1 - t) * currentPoints[i].x + t * currentPoints[i + 1].x;
                        const y = (1 - t) * currentPoints[i].y + t * currentPoints[i + 1].y;
                        newPoints.push({ x, y });
                    }
                    currentPoints = newPoints;
                }
                return currentPoints[0];
            }
        }

        // Simulate human-like mouse movement with acceleration, deceleration, and pauses
        function simulateMouseMovement(curve, callback) {
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;
            function ensureInViewport(coord) {
                return { x: Math.max(0, Math.min(coord.x, viewportWidth)), y: Math.max(0, Math.min(coord.y, viewportHeight)) };
            }
            const numSteps = 100;
            let length = 0;
            let prevPoint = curve.start;
            for (let i = 1; i <= numSteps; i++) {
                const t = i / numSteps;
                const point = getPointOnBezierCurve(curve, t);
                length += Math.sqrt(Math.pow(point.x - prevPoint.x, 2) + Math.pow(point.y - prevPoint.y, 2));
                prevPoint = point;
            }
            const baseSpeed = 500 + Math.random() * 1000; // 500-1500 px/s
            const duration = length / baseSpeed * 1000; // Total duration in ms
            const steps = Math.max(50, Math.ceil(duration / 10)); // At least 50 steps, ~10ms per step
            let step = 0;
            const initialDelay = 100 + Math.random() * 300; // Initial delay 100-400ms

            setTimeout(function moveStep() {
                if (step <= steps) {
                    const t = step / steps;
                    // Add acceleration/deceleration using ease-in-out
                    const easedT = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
                    const point = ensureInViewport(getPointOnBezierCurve(curve, easedT));
                    const mouseEvent = new MouseEvent('mousemove', {
                        clientX: point.x,
                        clientY: point.y,
                        bubbles: true,
                        cancelable: true
                    });
                    document.elementFromPoint(point.x, point.y)?.dispatchEvent(mouseEvent);
                    document.dispatchEvent(mouseEvent);
                    // Random pause every 10-20 steps to mimic human hesitation
                    const pause = Math.random() < 0.1 ? 50 + Math.random() * 100 : 0;
                    const nextStepTime = (duration / steps) + (Math.random() * 10 - 5) + pause;
                    setTimeout(moveStep, nextStepTime);
                    step++;
                } else if (callback) callback();
            }, initialDelay);
        }

        // Get the center point of an element
        function getElementCenter(element) {
            const rect = element.getBoundingClientRect();
            return { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
        }
    """

def build_typing_simulation(message):
    """Generate JavaScript for human-like typing simulation."""
    escaped_message = escape_for_applescript(message)
    return f"""
        // Simulate human-like typing with variable speed and pauses
        function simulateTyping(inputField, text) {{
            return new Promise(resolve => {{
                let currentText = '';
                let charIndex = 0;
                const textArray = text.split('');
                const typingInterval = setInterval(() => {{
                    if (charIndex < textArray.length) {{
                        currentText += textArray[charIndex];
                        if (inputField.tagName.toLowerCase() === 'textarea') {{
                            inputField.value = currentText;
                        }} else {{
                            inputField.innerHTML = currentText;
                        }}
                        const inputEvent = new Event('input', {{ bubbles: true }});
                        const changeEvent = new Event('change', {{ bubbles: true }});
                        inputField.dispatchEvent(inputEvent);
                        inputField.dispatchEvent(changeEvent);
                        charIndex++;
                        // Add random pauses to mimic human typing
                        const pauseChance = Math.random();
                        if (pauseChance < 0.2) {{ // 20% chance of a pause
                            setTimeout(() => {{}}, 200 + Math.random() * 300);
                        }}
                    }} else {{
                        clearInterval(typingInterval);
                        resolve();
                    }}
                }}, 50 + Math.random() * 100); // Typing speed between 50-150ms per character
            }});
        }}
        // Start typing simulation
        return simulateTyping(inputField, "{escaped_message}");
    """

def build_input_action(message):
    """Generate JavaScript for simplified input action that avoids AppleScript syntax issues."""
    escaped_message = escape_for_applescript(message)
    return f"""
        // Find input field 
        const inputField = document.querySelector('textarea') || 
                          document.querySelector('div[contenteditable=\\"true\\"]');
        
        if (!inputField) {{
            return 'Input field not found';
        }}
        
        // Focus the field
        inputField.focus();
        
        // Set value
        if (inputField.tagName && inputField.tagName.toLowerCase() === 'textarea') {{
            inputField.value = "{escaped_message}";
        }} else {{
            inputField.textContent = "{escaped_message}";
        }}
        
        // Trigger input events
        inputField.dispatchEvent(new Event('input', {{ bubbles: true }}));
        inputField.dispatchEvent(new Event('change', {{ bubbles: true }}));
        
        // Allow time for input to register
        setTimeout(function() {{
            // Find send button
            const sendButton = document.querySelector('button[type=\\"submit\\"]') || 
                             document.querySelector('button.send') ||
                             document.querySelector('button[aria-label=\\"Send\\"]') ||
                             document.querySelector('button:has(svg)');
            
            if (sendButton) {{
                // Click send button
                sendButton.click();
                return 'Message sent via button';
            }} else {{
                // Press Enter key
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
        }}, 500);
    """

def build_response_capture():
    """Generate JavaScript for capturing the response from Qwen."""
    return """
        // Create a representation of the conversation
        const conversation = {
            conversation: [],
            pageTitle: document.title,
            url: window.location.href,
            capturedAt: new Date().toISOString()
        };

        // Find all chat items (messages) on page
        const userMessages = document.querySelectorAll('.chat-item-user, .user-message, .user');
        const assistantMessages = document.querySelectorAll('.chat-item-assistant, .assistant-message, .assistant, .ai-message, .markdown-content-container, .prose');
        
        // Add all chat messages to the conversation
        if (userMessages && userMessages.length > 0) {
            for (const msg of userMessages) {
                conversation.conversation.push({
                    role: 'user',
                    content: msg.innerText || msg.textContent || 'No content found'
                });
            }
        }
        
        if (assistantMessages && assistantMessages.length > 0) {
            for (const msg of assistantMessages) {
                conversation.conversation.push({
                    role: 'assistant',
                    content: msg.innerText || msg.textContent || 'No content found'
                });
            }
        }
        
        // If no structured conversation found, try specific platform patterns
        if (conversation.conversation.length === 0) {
            // Qwen pattern
            if (window.location.href.includes('qwen.ai')) {
                const responseContainer = document.querySelector('#response-content-container, .markdown-content-container');
                if (responseContainer) {
                    conversation.response = responseContainer.innerText || responseContainer.textContent || 'No content found';
                }
            } 
            // Perplexity pattern
            else if (window.location.href.includes('perplexity.ai')) {
                const proseContainer = document.querySelector('.prose');
                if (proseContainer) {
                    conversation.response = proseContainer.innerText || proseContainer.textContent || 'No content found';
                }
            }
            // Generic fallback
            else {
                conversation.response = document.body.innerText || document.body.textContent || 'No content found';
            }
        }

        return JSON.stringify(conversation);
    """

def assemble_applescript_send_message(message, url="https://chat.qwen.ai/"):
    """Assemble AppleScript for sending a message."""
    return f"""
    tell application "Google Chrome"
        activate
        set foundTab to false
        set targetURL to "{url}"
        
        -- Loop through all windows and tabs to find the target tab
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
        
        if not foundTab then
            -- If tab not found, create a new one
            tell front window
                make new tab with properties {{URL:"{url}"}}
            end tell
            delay 3 -- Wait for page to load
        end if
        
        tell active tab of front window
            execute javascript "
                (function() {{
                    if (document.readyState !== 'complete') {{
                        return 'DOM not ready';
                    }}
                    {build_input_action(message)}
                }})();
            "
        end tell
    end tell
    """

def assemble_applescript_capture_response(url="https://chat.qwen.ai/"):
    """Assemble AppleScript for capturing the response."""
    return f"""
    tell application "Google Chrome"
        activate
        set foundTab to false
        set targetURL to "{url}"
        
        -- Loop through all windows and tabs to find the target tab
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
        
        tell active tab of front window
            execute javascript "
                (function() {{
                    {build_response_capture()}
                }})();
            "
        end tell
    end tell
    """

def ask_llm_question(message, url="https://chat.qwen.ai/", output_dir="./responses", wait_time=30):
    """
    Send a question to the LLM and retrieve the response.
    Args:
        message (str): The question to ask.
        url (str): The target URL of the LLM.
        output_dir (str): Directory to save responses.
        wait_time (int): Time to wait for response in seconds.
    Returns:
        dict: The response data or string of response text.
    """
    try:
        # Step 1: Send the message
        send_script = assemble_applescript_send_message(message, url)
        logger.info(f"Sending question: '{message}'")
        process = subprocess.run(["osascript", "-e", send_script], capture_output=True, text=True)
        if process.returncode != 0:
            logger.error(f"Failed to send message: {process.stderr}")
            return {"error": f"Failed to send message: {process.stderr}"}

        logger.info(f"Message sent successfully: {process.stdout}")

        # Step 2: Wait for the response
        logger.info(f"Waiting {wait_time} seconds for response...")
        time.sleep(wait_time)  # Wait for the response to complete

        # Step 3: Capture the response
        capture_script = assemble_applescript_capture_response(url)
        capture_process = subprocess.run(["osascript", "-e", capture_script], capture_output=True, text=True)
        if capture_process.returncode != 0:
            logger.error(f"Failed to capture response: {capture_process.stderr}")
            return {"error": f"Failed to capture response: {capture_process.stderr}"}

        # Parse the response
        try:
            response_json = capture_process.stdout.strip()
            response_data = json.loads(response_json)
            logger.info("Response captured successfully")

            # Extract the most relevant response text
            response_text = ""
            
            # First try to get the last assistant message
            if "conversation" in response_data and response_data["conversation"]:
                assistant_messages = [msg for msg in response_data["conversation"] if msg.get("role") == "assistant"]
                if assistant_messages:
                    response_text = assistant_messages[-1].get("content", "")
            
            # If we didn't find a structured message, try direct response field
            if not response_text and "response" in response_data:
                response_text = response_data["response"]
            
            # Save the full response to a file
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            safe_query = re.sub(r'[^a-zA-Z0-9]', '_', message[:30])
            filename = f"{timestamp}_{safe_query}.json"
            with open(f"{output_dir}/{filename}", 'w') as f:
                json.dump(response_data, f, indent=2)
            logger.info(f"Full response saved to {output_dir}/{filename}")
            
            # Also save just the text for easier use
            txt_filename = f"{timestamp}_{safe_query}.txt"
            with open(f"{output_dir}/{txt_filename}", 'w') as f:
                f.write(f"Question: {message}\n\n")
                f.write(f"Response:\n\n")
                f.write(response_text)
            logger.info(f"Text response saved to {output_dir}/{txt_filename}")

            # Return both the full data and easy to use text
            return {"data": response_data, "text": response_text}
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response as JSON: {e}")
            # Try to save whatever we got as raw text
            raw_output = capture_process.stdout.strip()
            
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            safe_query = re.sub(r'[^a-zA-Z0-9]', '_', message[:30])
            filename = f"{timestamp}_{safe_query}_raw.txt"
            with open(f"{output_dir}/{filename}", 'w') as f:
                f.write(raw_output)
            
            logger.info(f"Saved raw response to {output_dir}/{filename}")
            return raw_output

    except Exception as e:
        logger.error(f"Error during automation: {str(e)}")
        return {"error": str(e)}

def main():
    """Simple CLI interface for testing."""
    if len(sys.argv) < 2:
        print("Usage: python fixed_script.py 'Your question here' [url] [wait_time]")
        sys.exit(1)
        
    # Get arguments
    question = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else "https://chat.qwen.ai/"
    wait_time = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    
    # Ask the question
    response = ask_llm_question(question, url, wait_time=wait_time)
    
    # Display the response
    if isinstance(response, dict):
        if "error" in response:
            print(f"Error: {response['error']}")
        elif "text" in response:
            print("\n--- Response ---")
            print(response["text"])
            print("-----------------")
        else:
            print("\n--- Response Data ---")
            print(json.dumps(response, indent=2))
            print("---------------------")
    else:
        print("\n--- Raw Response ---")
        print(response)
        print("--------------------")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())