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
logger.add(
    sys.stdout,
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
)

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


def ask_llm_question(
    message: str,
    url: str = "https://chat.qwen.ai/",
    output_dir: str = "./responses",
    capture_html: bool = False,
):
    """
    Send a question to the LLM and retrieve the response.
    """
    try:
        # Step 1: Execute the send message AppleScript
        logger.info(f"Sending question: '{message}'")
        process = subprocess.run(
            ["osascript", "send_message.applescript", message],
            capture_output=True,
            text=True,
        )
        if process.returncode != 0:
            logger.error(f"Failed to send message: {process.stderr}")
            return {"error": f"Failed to send message: {process.stderr}"}

        logger.info(f"Message sent successfully: {process.stdout}")

        # Step 2: Wait for the response
        time.sleep(15)

        # Step 3: Execute the capture response AppleScript
        capture_process = subprocess.run(
            ["osascript", "capture_response.applescript"],
            capture_output=True,
            text=True,
        )
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
            safe_query = re.sub(r"[^a-zA-Z0-9]", "_", message[:30])
            filename = f"{timestamp}_{safe_query}.json"
            with open(f"{output_dir}/{filename}", "w") as f:
                json.dump(response_data, f, indent=2)
            logger.info(f"Response saved to {output_dir}/{filename}")

            return response_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response as JSON: {e}")
            return {
                "error": "Failed to parse response",
                "raw_output": capture_process.stdout.strip(),
            }

    except Exception as e:
        logger.error(f"Error during automation: {str(e)}")
        return {"error": str(e)}


@app.command()
def ask(
    question: Optional[str] = typer.Option(
        None, "--question", "-q", help="Question to ask the LLM"
    ),
    debug: bool = typer.Option(
        False, "--debug", "-d", help="Use a random debug question"
    ),
    url: str = typer.Option(
        "https://chat.qwen.ai/", "--url", "-u", help="Target URL of the LLM"
    ),
    output_dir: str = typer.Option(
        "./responses", "--output-dir", "-o", help="Directory to save responses"
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Run in interactive mode"
    ),
    capture_html: bool = typer.Option(
        False, "--capture-html", "-c", help="Capture the full HTML of the page"
    ),
):
    """
    Ask a question to a website-based LLM and retrieve the response.
    """
    if interactive:
        run_interactive_mode(url, output_dir, capture_html)
        return

    # Determine the question to ask
    if question:
        query = question
        logger.info(f"Using provided question: {query}")
    elif debug:
        query = get_debug_question()
        logger.info(f"Using debug question: {query}")
    else:
        logger.error(
            "No question provided. Use --question or --debug, or run in --interactive mode."
        )
        raise typer.Exit(code=1)

    # Ask the question and get the response
    response = ask_llm_question(query, url, output_dir, capture_html)

    # Display the last assistant response
    if "error" not in response and "conversation" in response:
        last_message = next(
            (
                msg
                for msg in reversed(response["conversation"])
                if msg.get("role") == "assistant"
            ),
            None,
        )
        if last_message:
            logger.info("Assistant Response:")
            logger.info(
                last_message.get("response", last_message.get("content", "No content"))
            )
    elif "error" in response:
        logger.error(f"Error: {response['error']}")
    else:
        logger.warning("No structured conversation found in response.")
        logger.info(f"Raw response: {response}")


def run_interactive_mode(url: str, output_dir: str, capture_html: bool):
    """
    Run in interactive CLI mode.
    """
    logger.info("===== Chat AI Automation Tool - Interactive Mode =====")
    logger.info(f"Target URL: {url}")
    logger.info("Type your questions below. Commands:")
    logger.info("  !debug  - Ask a random debug question")
    logger.info("  !exit   - Exit the program")
    logger.info("  !help   - Show this help message")
    logger.info("  !html   - Toggle HTML capture (current: {capture_html})")
    logger.info("======================================================")

    html_capture = capture_html
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
                logger.info("  !html   - Toggle HTML capture")
                logger.info("===================")
                continue
            elif user_input.lower() == "!debug":
                query = get_debug_question()
                logger.info(f"Using debug question: {query}")
            elif user_input.lower() == "!html":
                html_capture = not html_capture
                logger.info(f"HTML capture toggled to: {html_capture}")
                continue
            else:
                query = user_input
                logger.info(f"Using question: {query}")

            # Ask the question and get the response
            response = ask_llm_question(query, url, output_dir, html_capture)

            # Display the last assistant response
            if "error" not in response and "conversation" in response:
                last_message = next(
                    (
                        msg
                        for msg in reversed(response["conversation"])
                        if msg.get("role") == "assistant"
                    ),
                    None,
                )
                if last_message:
                    logger.info("\n--- Assistant Response ---")
                    logger.info(
                        last_message.get(
                            "response", last_message.get("content", "No content")
                        )
                    )
                    logger.info("--------------------------")
                if "html" in response:
                    logger.info(
                        "HTML captured (saved in file, too large to display here)"
                    )
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
