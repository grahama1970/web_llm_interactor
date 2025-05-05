import subprocess
import time
import logging
import random
import argparse
import sys
import json
from pathlib import Path
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# List of simple, non-suspicious questions for randomization
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


def get_random_question():
    """
    Return a random simple question from the predefined list.
    """
    return random.choice(SIMPLE_QUESTIONS)


def generate_applescript(message, url="https://chat.qwen.ai/", detect_completion=False):
    """
    Generate an AppleScript string to inject JavaScript into Chrome.
    Args:
        message (str): The text to send.
        url (str): The target URL to find in Chrome tabs.
        detect_completion (bool): Whether to wait for response completion and copy to clipboard.
    Returns:
        str: The AppleScript code.
    """
    # Double escape all quotes for JavaScript within AppleScript
    escaped_message = message.replace('\\', '\\\\').replace('"', '\\\\"').replace('\n', '\\\\n')
    
    # Additional JavaScript for detecting completion and copying to clipboard if requested
    completion_detection = "" if not detect_completion else """
    // Function to detect when response is complete and copy to clipboard
    function waitForResponseCompletion() {
        return new Promise(resolve => {
            console.log('Starting response detection');
            
            // Get all messages at the time we start looking
            let initialMessageCount = getMessageElements().length;
            console.log('Initial message count:', initialMessageCount);
            
            // Function to find all message elements using various possible selectors
            function getMessageElements() {
                // Different chat UIs use different selectors - try multiple common patterns
                const possibleContainerSelectors = [
                    // Generic message containers
                    '.conversation-turn', '.message-container', '.chat-message', '.message', 
                    // Perplexity-specific selectors
                    '.CornerTriangle', '.ProseMirror', 
                    // Qwen-specific selectors
                    '.chat-item', '.chat-message-item',
                    // Claude-specific selectors
                    '.claude-message', 
                    // Generic content holders
                    'div[role="presentation"]', '[data-message]'
                ];
                
                let allMessages = [];
                
                for (const selector of possibleContainerSelectors) {
                    const elements = document.querySelectorAll(selector);
                    if (elements && elements.length > 0) {
                        allMessages = [...allMessages, ...elements];
                    }
                }
                
                // Remove duplicates (in case multiple selectors match the same elements)
                return [...new Set(allMessages)];
            }
            
            // Function to find the latest assistant response element
            function findLatestAssistantResponse() {
                const elements = getMessageElements();
                const assistantIndicators = [
                    // Class-based indicators
                    'bot-message', 'assistant-message', 'ai-message', 
                    'response-message', 'claude-message',
                    // Attribute-based indicators
                    '[data-role="assistant"]', '[data-message-author-role="assistant"]'
                ];
                
                // First try specific assistant selectors
                for (const selector of assistantIndicators) {
                    const specificElements = document.querySelectorAll(selector);
                    if (specificElements && specificElements.length > 0) {
                        return specificElements[specificElements.length - 1];
                    }
                }
                
                // If no specific assistant elements found, try to infer from pattern
                // Typically user and assistant messages alternate, with assistant being even-indexed in many UIs
                if (elements.length >= initialMessageCount + 1) {
                    return elements[elements.length - 1];
                }
                
                // If we can't find a clear latest message, return null
                return null;
            }
            
            // Function to extract all conversation content
            function extractConversation() {
                const elements = getMessageElements();
                console.log('Found', elements.length, 'potential message elements');
                
                if (elements.length === 0) {
                    return { lastResponse: document.body.innerText };
                }
                
                const conversation = { conversation: [] };
                
                elements.forEach((element, index) => {
                    // Try to determine if user or assistant based on various attributes
                    const isEvenIndex = index % 2 === 0;
                    const hasUserIndicatorClass = element.classList.contains('user-message') || 
                                                element.classList.contains('user-turn') ||
                                                !!element.querySelector('.user');
                    const hasAssistantIndicatorClass = element.classList.contains('bot-message') || 
                                                     element.classList.contains('assistant-message') ||
                                                     !!element.querySelector('.assistant');
                    
                    // Determine role based on indicators, with fallback to alternating pattern
                    let role;
                    if (hasUserIndicatorClass) {
                        role = 'user';
                    } else if (hasAssistantIndicatorClass) {
                        role = 'assistant';
                    } else {
                        // Fallback to alternating pattern (common in many UIs)
                        role = isEvenIndex ? 'user' : 'assistant';
                    }
                    
                    // Try to extract content from various possible locations
                    let content = '';
                    const contentElement = element.querySelector('.message-content') || 
                                          element.querySelector('.content') ||
                                          element.querySelector('p') ||
                                          element;
                    
                    content = contentElement.innerText || contentElement.textContent || '';
                    
                    conversation.conversation.push({
                        role: role,
                        content: content.trim()
                    });
                });
                
                // Add entire page content as a backup
                conversation.fullPageText = document.body.innerText;
                
                return conversation;
            }
            
            // Function to monitor for response completion
            function monitorResponseCompletion() {
                console.log('Monitoring for response completion');
                let responseElem = findLatestAssistantResponse();
                let lastContent = responseElem ? (responseElem.innerText || '') : '';
                let lastDotCount = (lastContent.match(/\\./g) || []).length;
                let stableCount = 0;
                
                const contentChecker = setInterval(() => {
                    responseElem = findLatestAssistantResponse();
                    
                    if (!responseElem) {
                        console.log('No response element found yet');
                        return;
                    }
                    
                    const currentContent = responseElem.innerText || responseElem.textContent || '';
                    const currentDotCount = (currentContent.match(/\\./g) || []).length;
                    
                    // Check if content is stable or if we've reached a natural end (sentence end + stable)
                    const contentLengthStable = currentContent.length === lastContent.length;
                    const contentEndsWithPunctuation = /[.!?]\\s*$/.test(currentContent);
                    const noNewDots = currentDotCount === lastDotCount;
                    
                    if ((contentLengthStable && noNewDots) || 
                        (contentEndsWithPunctuation && currentContent.length > 20 && noNewDots)) {
                        stableCount++;
                        console.log(`Content appears stable (${stableCount}/3)`);
                        
                        if (stableCount >= 3) { // Content stable for 3 checks
                            clearInterval(contentChecker);
                            console.log('Response appears complete, extracting conversation');
                            
                            // Extract conversation data
                            const conversation = extractConversation();
                            
                            // Copy to clipboard using newer API with fallbacks
                            try {
                                // Modern clipboard API
                                const conversationJson = JSON.stringify(conversation, null, 2);
                                
                                // Try navigator.clipboard API first (modern, requires permission)
                                navigator.clipboard.writeText(conversationJson)
                                    .then(() => {
                                        console.log('Copied to clipboard with navigator.clipboard');
                                        resolve('Response completed and copied to clipboard');
                                    })
                                    .catch(err => {
                                        console.error('Navigator clipboard API failed:', err);
                                        
                                        // Fallback to execCommand (older method)
                                        try {
                                            // Create temporary element
                                            const el = document.createElement('textarea');
                                            el.value = conversationJson;
                                            el.setAttribute('readonly', '');
                                            el.style.position = 'absolute';
                                            el.style.left = '-9999px';
                                            document.body.appendChild(el);
                                            el.select();
                                            document.execCommand('copy');
                                            document.body.removeChild(el);
                                            console.log('Copied to clipboard with execCommand fallback');
                                            resolve('Response completed and copied to clipboard (fallback method)');
                                        } catch (execErr) {
                                            console.error('execCommand clipboard failed:', execErr);
                                            resolve('Response completed but clipboard copy failed. Data: ' + conversationJson.substring(0, 100) + '...');
                                        }
                                    });
                            } catch (e) {
                                console.error('Clipboard operations failed:', e);
                                resolve('Response completed but all clipboard methods failed');
                            }
                        }
                    } else {
                        console.log('Content still changing...');
                        lastContent = currentContent;
                        lastDotCount = currentDotCount;
                        stableCount = 0;
                    }
                }, 1000); // Check every second
            }
            
            // Set up observer to detect any DOM changes
            const bodyObserver = new MutationObserver((mutations) => {
                const currentMessageCount = getMessageElements().length;
                
                // If we detect a new message has been added
                if (currentMessageCount > initialMessageCount) {
                    console.log('New message detected, starting monitoring');
                    bodyObserver.disconnect();
                    monitorResponseCompletion();
                }
            });
            
            // Start observing with a broad configuration to catch all changes
            bodyObserver.observe(document.body, { 
                childList: true, 
                subtree: true,
                characterData: true,
                attributes: true
            });
            
            // Also start monitoring immediately in case the response is already there
            monitorResponseCompletion();
        });
    }
    """
    
    # Finalization code depending on whether to detect completion
    finalization = "resolve(`Button clicked with simulated mouse movement`);" if not detect_completion else """
    // Wait for response to complete then resolve
    waitForResponseCompletion().then(result => {
        resolve(result);
    });
    """
    
    script = '''
    tell application "Google Chrome"
        activate
        set foundTab to false
        set targetURL to "''' + url + '''"
        
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
            error "Could not find a tab with ''' + url + '''"
        end if
        
        -- Inject JavaScript to set the textarea value and submit
        tell active tab of front window
            execute javascript "
                (function() {
                    // Wait for DOM to be ready
                    if (document.readyState !== 'complete') {
                        return 'DOM not ready';
                    }
                    
                    // Target the textarea by ID or common selectors
                    let inputField = document.querySelector('textarea#chat-input') || 
                                    document.querySelector('textarea') ||
                                    document.querySelector('div[contenteditable=\\"true\\"]');
                    
                    if (!inputField) {
                        return 'Chat input field not found';
                    }
                    
                    // Function to create a random bezier curve for mouse movement
                    function createBezierCurve(startX, startY, endX, endY) {
                        // Create 1-3 control points for the bezier curve
                        const numControlPoints = Math.floor(Math.random() * 3) + 1;
                        const controlPoints = [];
                        
                        for (let i = 0; i < numControlPoints; i++) {
                            // Create random deviation
                            const midX = (startX + endX) / 2;
                            const midY = (startY + endY) / 2;
                            
                            // Random deviation up to 30% of distance
                            const maxDeviation = Math.sqrt(Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2)) * 0.3;
                            const deviation = Math.random() * maxDeviation;
                            const angle = Math.random() * 2 * Math.PI;
                            
                            controlPoints.push({
                                x: midX + deviation * Math.cos(angle),
                                y: midY + deviation * Math.sin(angle)
                            });
                        }
                        
                        return { 
                            start: { x: startX, y: startY },
                            end: { x: endX, y: endY },
                            controlPoints: controlPoints
                        };
                    }
                    
                    // Function to calculate point on curve at time t (0-1)
                    function getPointOnBezierCurve(curve, t) {
                        const { start, end, controlPoints } = curve;
                        
                        if (controlPoints.length === 1) {
                            // Quadratic Bezier curve
                            const cp = controlPoints[0];
                            const x = Math.pow(1 - t, 2) * start.x + 2 * (1 - t) * t * cp.x + Math.pow(t, 2) * end.x;
                            const y = Math.pow(1 - t, 2) * start.y + 2 * (1 - t) * t * cp.y + Math.pow(t, 2) * end.y;
                            return { x, y };
                        } else if (controlPoints.length === 2) {
                            // Cubic Bezier curve
                            const cp1 = controlPoints[0];
                            const cp2 = controlPoints[1];
                            const x = Math.pow(1 - t, 3) * start.x + 3 * Math.pow(1 - t, 2) * t * cp1.x + 3 * (1 - t) * Math.pow(t, 2) * cp2.x + Math.pow(t, 3) * end.x;
                            const y = Math.pow(1 - t, 3) * start.y + 3 * Math.pow(1 - t, 2) * t * cp1.y + 3 * (1 - t) * Math.pow(t, 2) * cp2.y + Math.pow(t, 3) * end.y;
                            return { x, y };
                        } else {
                            // Higher-order curve - simplified to direct line
                            const x = start.x + t * (end.x - start.x);
                            const y = start.y + t * (end.y - start.y);
                            return { x, y };
                        }
                    }
                    
                    // Function to simulate mouse movement along a bezier curve
                    function simulateMouseMovement(curve, callback) {
                        // Get rect of viewport
                        const viewportWidth = window.innerWidth;
                        const viewportHeight = window.innerHeight;
                        
                        // Ensure coordinates are within viewport
                        function ensureInViewport(coord) {
                            return {
                                x: Math.max(0, Math.min(coord.x, viewportWidth)),
                                y: Math.max(0, Math.min(coord.y, viewportHeight))
                            };
                        }
                        
                        // Calculate curve length approximately
                        const numSteps = 100;
                        let length = 0;
                        let prevPoint = curve.start;
                        
                        for (let i = 1; i <= numSteps; i++) {
                            const t = i / numSteps;
                            const point = getPointOnBezierCurve(curve, t);
                            length += Math.sqrt(Math.pow(point.x - prevPoint.x, 2) + Math.pow(point.y - prevPoint.y, 2));
                            prevPoint = point;
                        }
                        
                        // Calculate speed: 500-1500 pixels per second
                        const speed = 500 + Math.random() * 1000;
                        const duration = length / speed * 1000; // ms
                        
                        // Minimum 30 steps, more for longer movements
                        const steps = Math.max(30, Math.ceil(duration / 16));
                        let step = 0;
                        
                        // Add small random delay before movement (100-300ms)
                        const initialDelay = 100 + Math.random() * 200;
                        
                        setTimeout(function moveStep() {
                            if (step <= steps) {
                                const t = step / steps;
                                const point = ensureInViewport(getPointOnBezierCurve(curve, t));
                                
                                // Create and dispatch mouse event
                                const mouseEvent = new MouseEvent('mousemove', {
                                    clientX: point.x,
                                    clientY: point.y,
                                    bubbles: true,
                                    cancelable: true
                                });
                                
                                document.elementFromPoint(point.x, point.y)?.dispatchEvent(mouseEvent);
                                document.dispatchEvent(mouseEvent);
                                
                                // Add small random variation to timing (+-5ms)
                                const nextStepTime = duration / steps + (Math.random() * 10 - 5);
                                setTimeout(moveStep, nextStepTime);
                                step++;
                            } else {
                                // Movement complete
                                if (callback) callback();
                            }
                        }, initialDelay);
                    }
                    
                    // Function to get element center point
                    function getElementCenter(element) {
                        const rect = element.getBoundingClientRect();
                        return {
                            x: rect.left + rect.width / 2,
                            y: rect.top + rect.height / 2
                        };
                    }
                    ''' + completion_detection + '''
                    
                    // Random starting point near the edge of the screen
                    const edgePosition = Math.floor(Math.random() * 4); // 0: top, 1: right, 2: bottom, 3: left
                    const startX = edgePosition === 1 ? window.innerWidth - 10 : 
                                  edgePosition === 3 ? 10 : 
                                  Math.random() * window.innerWidth;
                    const startY = edgePosition === 0 ? 10 : 
                                  edgePosition === 2 ? window.innerHeight - 10 : 
                                  Math.random() * window.innerHeight;
                    
                    // Get target position (center of input field)
                    const targetPos = getElementCenter(inputField);
                    
                    // Create bezier curve for mouse movement
                    const curve = createBezierCurve(startX, startY, targetPos.x, targetPos.y);
                    
                    // Return a promise that resolves after the mouse movement
                    return new Promise(resolve => {
                        // Simulate mouse movement
                        simulateMouseMovement(curve, () => {
                            // Add small delay after movement (50-150ms)
                            setTimeout(() => {
                                // Click on input field
                                const clickEvent = new MouseEvent('click', {
                                    bubbles: true,
                                    cancelable: true,
                                    clientX: targetPos.x,
                                    clientY: targetPos.y
                                });
                                inputField.dispatchEvent(clickEvent);
                                
                                // Wait a bit after clicking (100-300ms)
                                setTimeout(() => {
                                    // Set the value for the textarea or contenteditable
                                    if (inputField.tagName.toLowerCase() === 'textarea') {
                                        inputField.value = \\"''' + escaped_message + '''\\";
                                    } else {
                                        inputField.innerHTML = \\"''' + escaped_message + '''\\";
                                    }
                                    
                                    // Simulate focus
                                    inputField.focus();
                                    
                                    // Trigger events to mimic user input
                                    let inputEvent = new Event('input', { bubbles: true });
                                    let changeEvent = new Event('change', { bubbles: true });
                                    inputField.dispatchEvent(inputEvent);
                                    inputField.dispatchEvent(changeEvent);
                                    
                                    // Generate random delay before submitting (300-1500ms)
                                    const submitDelay = 300 + Math.random() * 1200;
                                    
                                    setTimeout(() => {
                                        // Find and click the send button
                                        let sendButton = document.querySelector('button[type=\\"submit\\"]') || 
                                                        document.querySelector('button.send') ||
                                                        document.querySelector('button:has(svg)');
                                        
                                        if (sendButton) {
                                            // Move mouse to the send button using another bezier curve
                                            const sendButtonPos = getElementCenter(sendButton);
                                            const curveToButton = createBezierCurve(targetPos.x, targetPos.y, sendButtonPos.x, sendButtonPos.y);
                                            
                                            simulateMouseMovement(curveToButton, () => {
                                                // Click the send button
                                                const sendButtonClickEvent = new MouseEvent('click', {
                                                    bubbles: true,
                                                    cancelable: true,
                                                    clientX: sendButtonPos.x,
                                                    clientY: sendButtonPos.y
                                                });
                                                sendButton.dispatchEvent(sendButtonClickEvent);
                                                ''' + finalization + '''
                                            });
                                        } else {
                                            // If no button, try sending with Enter key
                                            let keydownEvent = new KeyboardEvent('keydown', {
                                                bubbles: true, 
                                                cancelable: true,
                                                key: 'Enter',
                                                code: 'Enter',
                                                keyCode: 13
                                            });
                                            
                                            inputField.dispatchEvent(keydownEvent);
                                            ''' + finalization + '''
                                        }
                                    }, submitDelay);
                                }, 100 + Math.random() * 200);
                            }, 50 + Math.random() * 100);
                        });
                    });
                })();
            "
        end tell
    end tell
    '''
    
    return script


def send_to_chat_window(message, wait_for_response=False, url="https://chat.qwen.ai/", output_dir="./responses"):
    """
    Execute AppleScript to send a message to the chat window.
    Args:
        message (str): The text to send.
        wait_for_response (bool): Whether to wait for response and copy to clipboard.
        url (str): The target URL to find in Chrome tabs.
        output_dir (str): Directory to save responses.
    Returns:
        dict or None: The response data if wait_for_response=True, otherwise None.
    """
    try:
        # First, just send the message
        send_script = generate_applescript(message, url=url, detect_completion=False)
        logging.info(f"Sending message: '{message}'")
        
        process = subprocess.run(
            ["osascript", "-e", send_script], capture_output=True, text=True
        )
        if process.returncode != 0:
            raise Exception(f"AppleScript error: {process.stderr}")

        logging.info(f"AppleScript output: {process.stdout}")
        print(f"Successfully sent message: '{message}'")

        # Wait for a short time to let the response start
        time.sleep(3)
        
        if wait_for_response:
            # For clipboard capture, use a simpler approach
            print("Waiting for response... (this may take a while)")
            
            # Wait a bit for the response to complete (most simple queries get answered in 10-15 seconds)
            wait_time = 15  # seconds
            print(f"Waiting {wait_time} seconds for response to complete...")
            time.sleep(wait_time)
            
            # Create a JavaScript file with the capture function
            capture_js_path = f"{output_dir}/capture_conversation.js"
            
            # Write the JavaScript functions to a file
            capture_js = '''
            // Function to get text content safely
            function getTextContent(element) {
                if (!element) return '';
                return element.innerText || element.textContent || '';
            }
            
            // Function to extract conversation from Qwen.ai
            function extractQwenConversation() {
                const conversation = {
                    platform: 'qwen.ai',
                    conversation: [],
                    pageTitle: document.title,
                    url: window.location.href,
                    capturedAt: new Date().toISOString()
                };
                
                // Get user messages (queries)
                const userMessages = document.querySelectorAll('.chat-item-user');
                if (userMessages && userMessages.length > 0) {
                    for (const msg of userMessages) {
                        conversation.conversation.push({
                            role: 'user',
                            content: getTextContent(msg)
                        });
                    }
                }
                
                // Find all thinking panels and response containers
                const thinkingPanels = document.querySelectorAll('.ThinkingPanel__Body__Content');
                const responseContainers = document.querySelectorAll('#response-content-container, .markdown-content-container');
                
                // Create pairs of thinking and response
                const maxLength = Math.max(
                    thinkingPanels ? thinkingPanels.length : 0,
                    responseContainers ? responseContainers.length : 0
                );
                
                for (let i = 0; i < maxLength; i++) {
                    const thinking = thinkingPanels && i < thinkingPanels.length 
                        ? getTextContent(thinkingPanels[i]) 
                        : '';
                        
                    const response = responseContainers && i < responseContainers.length 
                        ? getTextContent(responseContainers[i]) 
                        : '';
                    
                    conversation.conversation.push({
                        role: 'assistant',
                        thinking: thinking,
                        response: response
                    });
                }
                
                // If we don't have a complete conversation structure, capture at least what we have
                if (conversation.conversation.length === 0) {
                    const qwenThinkingPanel = document.querySelector('.ThinkingPanel__Body__Content');
                    const qwenResponseContainer = document.querySelector('#response-content-container');
                    
                    if (qwenThinkingPanel) {
                        conversation.thinking = getTextContent(qwenThinkingPanel);
                    }
                    
                    if (qwenResponseContainer) {
                        conversation.response = getTextContent(qwenResponseContainer);
                    }
                }
                
                return conversation;
            }
            
            // Function to extract conversation from generic chat platforms
            function extractGenericConversation() {
                const conversation = {
                    platform: 'generic',
                    conversation: [],
                    pageTitle: document.title,
                    url: window.location.href,
                    capturedAt: new Date().toISOString()
                };
                
                const messageElements = document.querySelectorAll('.message, .chat-message, .message-container, .chat-item');
                
                if (messageElements && messageElements.length > 0) {
                    for (let i = 0; i < messageElements.length; i++) {
                        const el = messageElements[i];
                        // Try to detect if it's user or assistant
                        const isUser = (el.classList.contains('user') || 
                                    el.classList.contains('user-message') ||
                                    !!el.querySelector('.user'));
                                    
                        conversation.conversation.push({
                            role: isUser ? 'user' : 'assistant',
                            content: getTextContent(el)
                        });
                    }
                } else {
                    // If we can't find message elements, capture the whole page
                    conversation.fullPageContent = document.body.innerText || document.body.textContent;
                }
                
                return conversation;
            }
            
            // Function to extract conversation from Perplexity.ai
            function extractPerplexityConversation() {
                const conversation = {
                    platform: 'perplexity.ai',
                    conversation: [],
                    pageTitle: document.title,
                    url: window.location.href,
                    capturedAt: new Date().toISOString()
                };
                
                // Specific selectors for Perplexity
                const queryBoxes = document.querySelectorAll('.query-box');
                const answerBoxes = document.querySelectorAll('.answer-box');
                
                // Process queries
                if (queryBoxes && queryBoxes.length > 0) {
                    for (const box of queryBoxes) {
                        conversation.conversation.push({
                            role: 'user',
                            content: getTextContent(box)
                        });
                    }
                }
                
                // Process answers
                if (answerBoxes && answerBoxes.length > 0) {
                    for (const box of answerBoxes) {
                        // Check for thinking content
                        const thinkingContent = box.querySelector('.thinking-content');
                        const answerContent = box.querySelector('.answer-content');
                        
                        if (thinkingContent && answerContent) {
                            conversation.conversation.push({
                                role: 'assistant',
                                thinking: getTextContent(thinkingContent),
                                response: getTextContent(answerContent)
                            });
                        } else {
                            conversation.conversation.push({
                                role: 'assistant',
                                content: getTextContent(box)
                            });
                        }
                    }
                }
                
                return conversation;
            }
            
            // Main function to capture conversation from any supported platform
            function captureConversation() {
                console.log("Capturing conversation from: " + window.location.href);
                
                // Detect platform and use appropriate extraction function
                if (window.location.href.includes('qwen.ai')) {
                    console.log("Detected Qwen.ai platform");
                    return extractQwenConversation();
                } 
                else if (window.location.href.includes('perplexity.ai')) {
                    console.log("Detected Perplexity.ai platform");
                    return extractPerplexityConversation();
                }
                else {
                    console.log("Using generic conversation extraction");
                    return extractGenericConversation();
                }
            }
            
            // Execute the capture function and return the result
            captureConversation();
            '''
            
            # Write the JS to a file
            with open(capture_js_path, 'w') as f:
                f.write(capture_js)
            
            # Now capture the entire conversation using the external JS file
            capture_script = f'''
            tell application "Google Chrome"
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
                
                if not foundTab then
                    error "Could not find a tab with {url}"
                end if
                
                tell active tab of front window
                    set jsResult to execute javascript (read file "{capture_js_path}" as string)
                    return jsResult
                end tell
            end tell
            '''
            
            capture_process = subprocess.run(
                ["osascript", "-e", capture_script], capture_output=True, text=True
            )
            
            if capture_process.returncode != 0:
                print(f"Error capturing response: {capture_process.stderr}")
                return None
                
            # Try to parse the output as JSON
            try:
                response_json = capture_process.stdout.strip()
                response_data = json.loads(response_json)
                print("Response captured successfully!")
                
                # Skip trying to copy to clipboard using shell since it's too complex
                # Just print a message that the data is available
                print("Data captured successfully - skipping clipboard operation")
                
                # Save a temporary file with the data that the user can access
                temp_file = f"{output_dir}/latest_response.json"
                with open(temp_file, 'w') as f:
                    json.dump(response_data, f, indent=2)
                print(f"Response data saved to {temp_file} for easy access")
                
                return response_data
            except json.JSONDecodeError:
                print("Failed to parse response as JSON")
                
                # Just capture the raw output as a fallback
                fallback_data = {
                    "raw_output": capture_process.stdout.strip()
                }
                return fallback_data
        else:
            # Just wait a bit if not waiting for response
            time.sleep(2)
            return None

    except Exception as e:
        logging.error(f"Error during automation: {str(e)}")
        print(f"Failed to send message: {str(e)}")
        return None


def save_response(response, query, output_dir="./responses"):
    """
    Save the response data to a file.
    Args:
        response (dict): The response data.
        query (str): The original query.
        output_dir (str): Directory to save responses.
    """
    if not response:
        return
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Create a timestamped filename with sanitized query
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    # Sanitize query for filename
    safe_query = re.sub(r'[^a-zA-Z0-9]', '_', query[:30])
    filename = f"{timestamp}_{safe_query}.json"
    
    # Save the response
    with open(f"{output_dir}/{filename}", 'w') as f:
        json.dump(response, f, indent=2)
    
    print(f"Response saved to {output_dir}/{filename}")


def main():
    """
    Main CLI function.
    """
    parser = argparse.ArgumentParser(description="Chat AI Automation Tool")
    
    parser.add_argument(
        "-q", "--query", 
        help="Custom query to send (if not provided, a random simple question will be used)"
    )
    
    parser.add_argument(
        "-r", "--random",
        action="store_true",
        help="Use a random simple question"
    )
    
    parser.add_argument(
        "-w", "--wait",
        action="store_true",
        help="Wait for response and copy to clipboard"
    )
    
    parser.add_argument(
        "-u", "--url",
        default="https://chat.qwen.ai/",
        help="Target URL (default: https://chat.qwen.ai/)"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        default="./responses",
        help="Directory to save responses (default: ./responses)"
    )
    
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    if len(sys.argv) == 1:
        # No arguments provided, show help and exit
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    if args.interactive:
        run_interactive_mode(args.url, args.output_dir)
    else:
        # Determine which query to use
        if args.query:
            query = args.query
        else:
            query = get_random_question()
            print(f"Using random question: {query}")
        
        # Send message and wait for response if requested
        response = send_to_chat_window(query, wait_for_response=args.wait, url=args.url, output_dir=args.output_dir)
        
        # Save response if we waited for it
        if args.wait and response:
            save_response(response, query, args.output_dir)


def run_interactive_mode(url, output_dir):
    """
    Run in interactive CLI mode.
    """
    print("\n===== Chat AI Automation Tool - Interactive Mode =====")
    print(f"Target URL: {url}")
    print("Type your queries below. Commands:")
    print("  !random  - Send a random simple question")
    print("  !exit    - Exit the program")
    print("  !help    - Show this help message")
    print("======================================================\n")
    
    while True:
        try:
            # Get input from user
            user_input = input("\nEnter query (or command): ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() == "!exit":
                print("Exiting...")
                break
                
            elif user_input.lower() == "!help":
                print("\n===== Commands =====")
                print("  !random  - Send a random simple question")
                print("  !exit    - Exit the program")
                print("  !help    - Show this help message")
                print("===================\n")
                continue
                
            elif user_input.lower() == "!random":
                query = get_random_question()
                print(f"Using random question: {query}")
            else:
                query = user_input
            
            # Always wait for response in interactive mode
            response = send_to_chat_window(query, wait_for_response=True, url=url, output_dir=output_dir)
            
            # Save response
            if response:
                save_response(response, query, output_dir)
                
                # Print last response for convenience
                if 'conversation' in response:
                    last_message = next((msg for msg in reversed(response['conversation']) 
                                         if msg.get('role') == 'assistant'), None)
                    if last_message:
                        print("\n--- Assistant Response ---")
                        print(last_message.get('content', 'No content'))
                        print("------------------------\n")
                elif 'lastResponse' in response:
                    print("\n--- Assistant Response ---")
                    print(response['lastResponse'])
                    print("------------------------\n")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
