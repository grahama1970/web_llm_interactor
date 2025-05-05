import pyautogui
import time
import webbrowser
import os
import logging
from pathlib import Path
from random import uniform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler("pyautogui_test.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# PyAutoGUI settings
pyautogui.PAUSE = 0.3  # Delay between actions
pyautogui.FAILSAFE = True  # Move mouse to top-left to abort


def mimic_human_typing(text):
    """Type text with randomized delays to mimic human typing."""
    for char in text:
        pyautogui.write(char)
        time.sleep(uniform(0.03, 0.1))
    time.sleep(uniform(0.5, 1.0))


def check_for_detection(html_content):
    """Check HTML for bot detection indicators."""
    indicators = [
        "captcha",
        "i'm not a robot",
        "cloudflare",
        "verify you are human",
        "access denied",
        "blocked",
        "forbidden",
        "security check",
        "rate limit",
    ]
    return any(indicator in html_content.lower() for indicator in indicators)


def get_input_coordinates():
    """Prompt user to find input field coordinates."""
    print(
        "Please maximize Chrome, navigate to https://www.perplexity.ai/, and wait for the page to load."
    )
    print(
        "Then, move your mouse to the input field (where you'd type your query) and press Enter."
    )
    print("You have 20 seconds to position the mouse...")
    time.sleep(20)
    x, y = pyautogui.position()
    print(f"Input field coordinates: ({x}, {y})")
    return x, y


def main():
    """Test PyAutoGUI automation on Perplexity AI with minimal automation."""
    url = "https://www.perplexity.ai/"
    query = "What is the capital of France?"
    output_html = Path("perplexity_test_output.html")
    max_attempts = 3
    timeout = 30

    logger.info("Starting PyAutoGUI test on Perplexity AI")
    print("Testing PyAutoGUI on Perplexity AI...")

    # Get input field coordinates
    print("First, let's find the input field coordinates.")
    input_x, input_y = get_input_coordinates()

    # Prompt to ensure Chrome is focused
    print("Please ensure Chrome is maximized and focused. Press Enter to continue...")
    input()  # Wait for user confirmation

    try:
        # Open Chrome and navigate to URL
        logger.info(f"Opening Chrome with URL: {url}")
        webbrowser.open(url)
        time.sleep(30)  # Increased wait for page load and UI rendering

        # Focus Chrome window
        logger.info("Focusing Chrome window")
        os.system("osascript -e 'tell application \"Google Chrome\" to activate'")
        time.sleep(3)

        # Handle potential modals (e.g., cookie consent)
        print(
            "If you see a cookie consent banner or modal, please close it and press Enter..."
        )
        input()

        # Prompt for manual click
        print(
            f"Please manually click the input field at ({input_x}, {input_y}) and press Enter to continue..."
        )
        input()

        # Type query
        logger.info(f"Typing query: {query}")
        mimic_human_typing(query)
        time.sleep(1)

        # Submit query
        logger.info("Submitting query with Enter key")
        pyautogui.press("enter")
        time.sleep(20)  # Wait for response

        # Save page source with retries
        for attempt in range(max_attempts):
            try:
                logger.info("Attempting to save page source")
                pyautogui.hotkey("cmd", "u")  # View source on macOS
                time.sleep(3)
                pyautogui.hotkey("cmd", "s")  # Save as
                time.sleep(2)
                mimic_human_typing(str(output_html))
                pyautogui.press("enter")
                time.sleep(3)
                pyautogui.hotkey("cmd", "w")  # Close source tab
                break
            except Exception as e:
                logger.warning(f"Save attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_attempts - 1:
                    raise
                time.sleep(2)

        # Analyze HTML
        if output_html.exists():
            with open(output_html, "r", encoding="utf-8") as f:
                html_content = f.read()
            logger.info(f"Saved HTML to {output_html} ({len(html_content)} bytes)")

            # Check if query was entered
            if query.lower() not in html_content.lower():
                logger.error("Query not found in HTML - interaction failed")
                print("Error: Query was not entered into the page")
                print(
                    "PyAutoGUI likely cannot interact with Perplexity due to bot detection or UI issues."
                )
                return

            # Check for detection
            if check_for_detection(html_content):
                logger.error("Bot detection indicators found in HTML")
                print("Bot detection triggered: CAPTCHA or error message found")
                print("PyAutoGUI was detected by Perplexity.")
                return

            # Check for response
            if (
                "capital of france" in html_content.lower()
                and "paris" in html_content.lower()
            ):
                logger.info("Response contains expected query and answer")
                print("Success: Response received, no obvious bot detection")
                print("PyAutoGUI worked successfully!")
            else:
                logger.warning("Response may be incomplete or blocked")
                print("Warning: Response may not contain expected content")
        else:
            logger.error("Failed to save HTML output")
            print("Error: Could not save page source")
            print("PyAutoGUI interaction may have failed.")

    except Exception as e:
        logger.error(f"Error during automation: {str(e)}")
        print(f"Error: Automation failed - {str(e)}")
        print(
            "PyAutoGUI likely cannot interact with Perplexity due to bot detection or UI issues."
        )


if __name__ == "__main__":
    main()
