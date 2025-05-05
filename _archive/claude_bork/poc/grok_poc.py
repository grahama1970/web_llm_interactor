import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def send_to_chat_window(message):
    """
    Use undetected-chromedriver to send a message to the Qwen chat window by launching the URL.
    Args:
        message (str): The text to send.
    """
    try:
        # Configure Chrome options
        options = uc.ChromeOptions()
        # options.add_argument("--headless")  # Uncomment for headless mode if needed
        options.add_argument("--disable-gpu")  # Improve stability on some systems
        options.add_argument("--no-sandbox")  # Bypass OS security for automation

        # Initialize the driver with undetected-chromedriver
        driver = uc.Chrome(options=options)
        logging.info("Launched new Chrome instance with undetected-chromedriver")

        # Navigate to the Qwen chat page
        driver.get("https://chat.qwen.ai/")
        logging.info("Navigated to https://chat.qwen.ai/")

        # Give some time for the page to load
        time.sleep(2)

        # Wait for the chat input field to be interactable
        try:
            chat_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//input[@placeholder='How can I help you today?']")
                )
            )
            logging.info("Found chat input field with placeholder")
        except:
            # Fallback to contenteditable div if input not found
            chat_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true']"))
            )
            logging.info("Found chat input field with contenteditable attribute")

        # Clear the input field (if needed)
        chat_input.clear()

        # Simulate human-like typing by sending keys one at a time with small delays
        for char in message:
            chat_input.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # Random delay between 50-150ms
        logging.info("Typed message into chat input")

        # Press Enter to send
        chat_input.send_keys(Keys.RETURN)
        logging.info("Pressed Enter to send message")

        print(f"Successfully sent message: '{message}'")

        # Wait a moment to see the result
        time.sleep(2)

        # Close the driver
        driver.quit()

    except Exception as e:
        logging.error(f"Error during automation: {str(e)}")
        print(f"Failed to send message: {str(e)}")
        if "driver" in locals():
            driver.quit()


if __name__ == "__main__":
    # Example message
    test_message = "Proof of concept: Python can paste into a chat window!"

    send_to_chat_window(test_message)
