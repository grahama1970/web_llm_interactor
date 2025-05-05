import subprocess
import time
import random
import sys
import json
from pathlib import Path
import re
from loguru import logger
import typer
from typing import Optional

# Configure Loguru logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

# List of simple questions for debugging purposes
SIMPLE_QUESTIONS = [
    "What is the capital of France?",
    "How tall is Mount Everest?",
    "What year was the Declaration of Independence signed?",
    "Who wrote Pride and Prejudice?",
    "What is the chemical symbol for gold?",
    "How many planets are in our solar system?",
    "What is the boiling point of water in Celsius?",
    "Who painted the Mona Lisa?",
    "What is the square root of 64?",
    "What's the largest mammal on Earth?",
    "How many continents are there?",
    "What's the formula for water?",
    "Who discovered gravity?",
    "What is 7 times 8?",
    "What's the capital of Japan?",
    "Which planet is closest to the sun?",
    "What is photosynthesis?",
    "Who was the first US President?",
    "What is the speed of light?",
    "How many sides does a hexagon have?",
]

app = typer.Typer()

def get_debug_question():
    """Return a random simple question for debugging purposes."""
    return random.choice(SIMPLE_QUESTIONS)

def escape_for_applescript(text):
    """Escape special characters for AppleScript and JavaScript compatibility."""
    return text.replace("\\", "\\\\").replace('"', '\\\\"').replace("\n", "\\\\n")

def build_tab_selection(url):
    """Generate AppleScript for selecting the target tab."""
    return f"""
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
            error "Could not find a tab with {url}"
        end if
    """

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
    """Generate JavaScript for input action with advanced human-like interaction."""
    return f"""
        // Target the textarea by ID or common selectors
        let inputField = document.querySelector('textarea#chat-input') || 
                        document.querySelector('textarea') ||
                        document.querySelector('div[contenteditable=\\"true\\"]');
        if (!inputField) {{
            return 'Chat input field not found';
        }}

        // Random starting point near the edge of the screen
        const edgePosition = Math.floor(Math.random() * 4); // 0: top, 1: right, 2: bottom, 3: left
        const startX = edgePosition === 1 ? window.innerWidth - 10 : 
                      edgePosition === 3 ? 10 : 
                      Math.random() * window.innerWidth;
        const startY = edgePosition === 0 ? 10 : 
                      edgePosition === 2 ? window.innerHeight - 10 : 
                      Math.random() * window.innerHeight;
        const targetPos = getElementCenter(inputField);

        // Create Bezier curve for mouse movement to input field
        const curve = createNaturalBezierCurve(startX, startY, targetPos.x, targetPos.y);
        return new Promise(resolve => {{
            simulateMouseMovement(curve, () => {{
                setTimeout(() => {{
                    const clickEvent = new MouseEvent('click', {{
                        bubbles: true,
                        cancelable: true,
                        clientX: targetPos.x,
                        clientY: targetPos.y
                    }}));
                    inputField.dispatchEvent(clickEvent);
                    inputField.focus();
                    setTimeout(() => {{
                        {build_typing_simulation(message)}
                        .then(() => {{
                            const submitDelay = 500 + Math.random() * 1000; // 500-1500ms pause before submitting
                            setTimeout(() => {{
                                let sendButton = document.querySelector('button[type=\\"submit\\"]') || 
                                                document.querySelector('button.send') ||
                                                document.querySelector('button:has(svg)');
                                if (sendButton) {{
                                    const sendButtonPos = getElementCenter(sendButton);
                                    const curveToButton = createNaturalBezierCurve(targetPos.x, targetPos.y, sendButtonPos.x, sendButtonPos.y);
                                    simulateMouseMovement(curveToButton, () => {{
                                        const sendButtonClickEvent = new MouseEvent('click', {{
                                            bubbles: true,
                                            cancelable: true,
                                            clientX: sendButtonPos.x,
                                            clientY: sendButtonPos.y
                                        }}));
                                        sendButton.dispatchEvent(sendButtonClickEvent);
                                        resolve('Message sent successfully');
                                    }});
                                }} else {{
                                    const keydownEvent = new KeyboardEvent('keydown', {{
                                        bubbles: true,
                                        cancelable: true,
                                        key: 'Enter',
                                        code: 'Enter',
                                        keyCode: 13
                                    }});
                                    inputField.dispatchEvent(keydownEvent);
                                    resolve('Message sent successfully via Enter key');
                                }}
                            }}, submitDelay);
                        }});
                    }}, 100 + Math.random() * 200);
                }}, 50 + Math.random() * 100);
            }});
        }});
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

        // Platform-specific selectors for Qwen.ai
        const qwenThinkingPanel = document.querySelector('.ThinkingPanel__Body__Content');
        const qwenResponseContainer = document.querySelector('#response-content-container');

        if (window.location.href.includes('qwen.ai') && (qwenThinkingPanel || qwenResponseContainer)) {
            conversation.platform = 'qwen.ai';
            conversation.conversation = [];

            // Get user messages (queries)
            const userMessages = document.querySelectorAll('.chat-item-user');
            if (userMessages && userMessages.length > 0) {
                for (const msg of userMessages) {
                    conversation.conversation.push({
                        role: 'user',
                        content: msg.innerText || msg.textContent || 'No content found'
                    });
                }
            }

            // Find all thinking panels and response containers
            const thinkingPanels = document.querySelectorAll('.ThinkingPanel__Body__Content');
            const responseContainers = document.querySelectorAll('#response-content-container, .markdown-content-container');

            const maxLength = Math.max(
                thinkingPanels ? thinkingPanels.length : 0,
                responseContainers ? responseContainers.length : 0
            );

            for (let i = 0; i < maxLength; i++) {
                const thinking = thinkingPanels && i < thinkingPanels.length 
                    ? thinkingPanels[i].innerText || thinkingPanels[i].textContent 
                    : '';
                const response = responseContainers && i < responseContainers.length 
                    ? responseContainers[i].innerText || responseContainers[i].textContent 
                    : '';
                conversation.conversation.push({
                    role: 'assistant',
                    thinking: thinking,
                    response: response
                });
            }

            if (conversation.conversation.length === 0) {
                if (qwenThinkingPanel) {
                    conversation.thinking = qwenThinkingPanel.innerText || qwenThinkingPanel.textContent;
                }
                if (qwenResponseContainer) {
                    conversation.response = qwenResponseContainer.innerText || qwenResponseContainer.textContent;
                }
            }
        } else {
            const messageElements = document.querySelectorAll('.message, .chat-message, .message-container, .chat-item');
            if (messageElements && messageElements.length > 0) {
                for (let i = 0; i < messageElements.length; i++) {
                    const el = messageElements[i];
                    const isUser = (el.classList.contains('user') || 
                                   el.classList.contains('user-message') ||
                                   !!el.querySelector('.user'));
                    conversation.conversation.push({
                        role: isUser ? 'user' : 'assistant',
                        content: el.innerText || el.textContent || 'No content found'
                    });
                }
            } else {
                conversation.fullPageContent = document.body.innerText || document.body.textContent;
            }
        }

        return JSON.stringify(conversation);
    """

def assemble_applescript_send_message(message, url="https://chat.qwen.ai/"):
    """Assemble AppleScript for sending a message."""
    return f"""
    tell application "Google Chrome"
        activate
        {build_tab_selection(url)}
        tell active tab of front window
            execute javascript "
                (function() {{
                    if (document.readyState !== 'complete') {{
                        return 'DOM not ready';
                    }}
                    {build_advanced_mouse_simulation()}
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
        {build_tab_selection(url)}
        tell active tab of front window
            execute javascript "
                (function() {{
                    {build_response_capture()}
                }})();
            "
        end tell
    end tell
    """

def ask_llm_question(message, url="https://chat.qwen.ai/", output_dir="./responses"):
    """
    Send a question to the LLM and retrieve the response.
    Args:
        message (str): The question to ask.
        url (str): The target URL of the LLM.
        output_dir (str): Directory to save responses.
    Returns:
        dict: The response data.
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
        time.sleep(15)  # Wait for the response to complete (adjust as needed)

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

            # Save the response to a file
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            safe_query = re.sub(r'[^a-zA-Z0-9]', '_', message[:30])
            filename = f"{timestamp}_{safe_query}.json"
            with open(f"{output_dir}/{filename}", 'w') as f:
                json.dump(response_data, f, indent=2)
            logger.info(f"Response saved to {output_dir}/{filename}")

            return response_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response as JSON: {e}")
            return {"error": "Failed to parse response", "raw_output": capture_process.stdout.strip()}

    except Exception as e:
        logger.error(f"Error during automation: {str(e)}")
        return {"error": str(e)}

@app.command()
def ask(
    question: Optional[str] = typer.Option(None, "--question", "-q", help="Question to ask the LLM"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Use a random debug question"),
    url: str = typer.Option("https://chat.qwen.ai/", "--url", "-u", help="Target URL of the LLM"),
    output_dir: str = typer.Option("./responses", "--output-dir", "-o", help="Directory to save responses"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Run in interactive mode")
):
    """
    Ask a question to a website-based LLM and retrieve the response.
    """
    if interactive:
        run_interactive_mode(url, output_dir)
        return

    # Determine the question to ask
    if question:
        query = question
        logger.info(f"Using provided question: {query}")
    elif debug:
        query = get_debug_question()
        logger.info(f"Using debug question: {query}")
    else:
        logger.error("No question provided. Use --question or --debug, or run in --interactive mode.")
        raise typer.Exit(code=1)

    # Ask the question and get the response
    response = ask_llm_question(query, url, output_dir)

    # Display the last assistant response
    if "error" not in response and "conversation" in response:
        last_message = next((msg for msg in reversed(response["conversation"]) if msg.get("role") == "assistant"), None)
        if last_message:
            logger.info("Assistant Response:")
            logger.info(last_message.get("response", last_message.get("content", "No content")))
    elif "error" in response:
        logger.error(f"Error: {response['error']}")
    else:
        logger.warning("No structured conversation found in response.")
        logger.info(f"Raw response: {response}")

def run_interactive_mode(url: str, output_dir: str):
    """
    Run in interactive CLI mode.
    """
    logger.info("===== Chat AI Automation Tool - Interactive Mode =====")
    logger.info(f"Target URL: {url}")
    logger.info("Type your questions below. Commands:")
    logger.info("  !debug  - Ask a random debug question")
    logger.info("  !exit   - Exit the program")
    logger.info("  !help   - Show this help message")
    logger.info("======================================================")

    while True:
        try:
            user_input = input("\nEnter question (or command): ").strip()
            if not user_input:
                continue
            elif user_input.lower() == "!exit":
                logger.info("Exiting...")
                break
            elif user_input.lower() == "!help":
                logger.info("\n===== Commands =====")
                logger.info("  !debug  - Ask a random debug question")
                logger.info("  !exit   - Exit the program")
                logger.info("  !help   - Show this help message")
                logger.info("===================")
                continue
            elif user_input.lower() == "!debug":
                query = get_debug_question()
                logger.info(f"Using debug question: {query}")
            else:
                query = user_input
                logger.info(f"Using question: {query}")

            # Ask the question and get the response
            response = ask_llm_question(query, url, output_dir)

            # Display the last assistant response
            if "error" not in response and "conversation" in response:
                last_message = next((msg for msg in reversed(response["conversation"]) if msg.get("role") == "assistant"), None)
                if last_message:
                    logger.info("\n--- Assistant Response ---")
                    logger.info(last_message.get("response", last_message.get("content", "No content")))
                    logger.info("--------------------------")
            elif "error" in response:
                logger.error(f"Error: {response['error']}")
            else:
                logger.warning("No structured conversation found in response.")
                logger.info(f"Raw response: {response}")

        except KeyboardInterrupt:
            logger.info("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {str(e)}")

if __name__ == "__main__":
    app()