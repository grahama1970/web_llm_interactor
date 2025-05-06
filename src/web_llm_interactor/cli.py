"""
web-llm-interactor: Interact with web-based LLMs (like Qwen, Perplexity, etc.) from the command line or agent scripts.

Send a message to a web chat LLM, extract the structured JSON response, and use it in your agent or workflow.

===============================================================
INSTALLATION & USAGE
===============================================================

INSTALLATION:
  uv pip install .              # Install from current directory using uv (recommended)
  uv pip install web-llm-interactor  # Install from PyPI (when published)

USAGE:
  web-llm-interactor ask "Your question here"  # Basic usage (uses Qwen by default)
  
  # Before running, make sure to open the target URL in Google Chrome!

COMMON EXAMPLES:
  web-llm-interactor ask "What is the capital of Georgia?"
  web-llm-interactor ask "Who is the CEO of Apple?" --url "https://chat.perplexity.ai/" --output-html "./perplexity_response.html"
  web-llm-interactor ask "What is the capital of Florida?" --all

DEVELOPMENT MODE (not for end users):
  python -m web_llm_interactor.cli ask "Your question"
  uv run src/web_llm_interactor/cli.py ask "Your question"

Use --help on any command for more details.
"""

import typer
import subprocess
import time
import os
from pathlib import Path
from web_llm_interactor.file_utils import generate_html_filename

DEFAULT_SCRIPT_PATH = Path(__file__).parent / "send_enter_save_source.applescript"
DEFAULT_HTML_PATH = Path("output.html").resolve()
DEFAULT_URL = "https://chat.qwen.ai/"

app = typer.Typer(
    help="""
web-llm-interactor: Interact with web-based LLMs (like Qwen, Perplexity, etc.) from the command line or agent scripts.

Send a message to a web chat LLM, extract the structured JSON response, and use it in your agent or workflow.

IMPORTANT: Before running, make sure to open the target URL in Google Chrome!

USAGE:
  web-llm-interactor ask "Your question here"  # Basic usage (uses Qwen by default)

Examples:
  web-llm-interactor ask "What is the capital of Georgia?"
  web-llm-interactor ask "Who is the CEO of Apple?" --url "https://chat.perplexity.ai/" --output-html "./perplexity_response.html"
  web-llm-interactor ask "What is the capital of Florida?" --all
"""
)

DEFAULT_SCRIPT_PATH = Path(__file__).parent / "send_enter_save_source.applescript"
DEFAULT_HTML_PATH = Path("output.html").resolve()
DEFAULT_URL = "https://chat.qwen.ai/"


@app.command(
    help="Send a message to a web LLM chat page and extract the JSON response."
)
def ask(
    question: str = typer.Argument(
        ..., help="The message/question to send to the web LLM."
    ),
    url: str = typer.Option(
        DEFAULT_URL,
        "--url",
        "-u",
        help="Target chat URL (e.g., https://chat.qwen.ai/).",
    ),
    output_html: Path = typer.Option(
        None,
        "--output-html",
        "-o",
        help="Path to save the output HTML file. If not provided, a unique filename will be generated.",
    ),
    all: bool = typer.Option(
        False, "--all", help="Return all JSON objects, not just the last one."
    ),
    script_path: Path = typer.Option(
        DEFAULT_SCRIPT_PATH, "--applescript", help="Path to the AppleScript file."
    ),
    max_attempts: int = typer.Option(
        3, "--max-attempts", help="Maximum retry attempts for response."
    ),
    timeout: int = typer.Option(
        30, "--timeout", help="Timeout per attempt in seconds."
    ),
    poll_interval: int = typer.Option(
        2, "--poll-interval", help="Interval in seconds between polling for response completion."
    ),
    stable_polls: int = typer.Option(
        3, "--stable-polls", help="Number of stable polls required to consider response complete."
    ),
    json_format: bool = typer.Option(
        True, "--json-format/--no-json-format", help="Append JSON format instructions to the query."
    ),
    required_fields: str = typer.Option(
        "question,thinking,answer", "--fields", help="Comma-separated list of fields required in the JSON response."
    ),
    selector: str = typer.Option(
        None, "--selector", help="CSS selector for the chat input field."
    ),
):
    """
    Send a message to a web LLM chat page and extract the JSON response.
    """
    # Generate a unique filename if not provided
    if output_html is None:
        output_html = generate_html_filename(question, url)
        typer.echo(f"Saving HTML to: {output_html}")
    
    # Append JSON format instructions if enabled
    formatted_question = question
    if json_format:
        json_format_instruction = f" Return in well-ordered JSON with fields: {required_fields}"
        if not question.strip().endswith(json_format_instruction):
            formatted_question = f"{question}{json_format_instruction}"
        typer.echo(f"Added JSON format instructions. Fields: {required_fields}")
    
    typer.echo(f"Sending: {formatted_question}")
    for attempt in range(max_attempts):
        try:
            # Set environment variables for AppleScript
            env = os.environ.copy()
            env["RESPONSE_WAIT_TIME"] = str(timeout)
            env["POLL_INTERVAL"] = str(poll_interval)
            env["REQUIRED_STABLE_POLLS"] = str(stable_polls)
            
            if selector:
                env["CHAT_INPUT_SELECTOR"] = selector
            
            args = [
                "osascript",
                str(script_path),
                formatted_question,
                url,
                str(output_html),
            ]
            if all:
                args.append("--all")
            
            # Add fields argument for extract_json_from_html.py
            args.append("--fields")
            args.append(required_fields)
            
            typer.echo(f"Using HTML length polling: max wait={timeout}s, poll interval={poll_interval}s, stable polls={stable_polls}")
            
            result = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True,
                timeout=timeout + 10,  # Add a small buffer to the subprocess timeout
                env=env,
            )
            output = result.stdout.strip()
            if not output or output == "{}":
                typer.secho(
                    f"Warning: Empty response received. Retrying ({attempt + 1}/{max_attempts})..."
                    if attempt < max_attempts - 1
                    else "Error: Empty response received after max attempts.",
                    fg=typer.colors.RED,
                )
                if attempt == max_attempts - 1:
                    raise typer.Exit(code=1)
                time.sleep(2)
                continue
            typer.echo("Result from web LLM:")
            typer.echo(output)
            return
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip()
            if "Could not find an open tab" in error_msg:
                typer.secho(
                    f"Error: No Chrome tab found with URL {url}. Please open the URL in Chrome.",
                    fg=typer.colors.RED,
                )
            elif "Page HTML was empty" in error_msg:
                typer.secho(
                    f"Error: No response received. Retrying ({attempt + 1}/{max_attempts})..."
                    if attempt < max_attempts - 1
                    else "Error: No response received after max attempts.",
                    fg=typer.colors.RED,
                )
            else:
                typer.secho(f"AppleScript Error: {error_msg}", fg=typer.colors.RED)
            if attempt == max_attempts - 1:
                raise typer.Exit(code=1)
        except subprocess.TimeoutExpired:
            typer.secho(
                f"Error: Timeout after {timeout}s. Retrying ({attempt + 1}/{max_attempts})..."
                if attempt < max_attempts - 1
                else f"Error: Timeout after {timeout}s after max attempts.",
                fg=typer.colors.RED,
            )
            if attempt == max_attempts - 1:
                raise typer.Exit(code=1)
            time.sleep(2)


@app.command("usage", help="Show usage examples for this CLI.")
def usage():
    """
    Show usage examples for web-llm-interactor.
    """
    examples = """
Examples:
  web-llm-interactor ask "What is the capital of Georgia?"
  web-llm-interactor ask "Who is the CEO of Apple?" --url "https://chat.perplexity.ai/" --output-html "./perplexity_response.html"
  web-llm-interactor ask "What is the capital of Florida?" --all
  web-llm-interactor ask "Explain quantum computing" --fields "question,answer"
  web-llm-interactor ask "What's the weather like in Paris?" --no-json-format
  web-llm-interactor ask "List the planets in our solar system" --timeout 45
  web-llm-interactor ask "How does photosynthesis work?" --selector "textarea.chat-input"

Arguments:
  question           The question or message to send to the LLM.

Options:
  --url, -u          The target chat URL (default: https://chat.qwen.ai/)
  --output-html, -o  Path to save the output HTML file (default: ./output.html)
  --all              Return all JSON objects, not just the last one.
  --applescript      Path to the AppleScript file to use.
  --max-attempts     Maximum retry attempts for response (default: 3)
  --timeout          Timeout per attempt in seconds (default: 30)
  --json-format      Append JSON format instructions to the query (default: enabled)
  --no-json-format   Don't append JSON format instructions
  --fields           Comma-separated list of required fields (default: "question,thinking,answer")
  --selector         CSS selector for the chat input field (default: "textarea#chat-input.text-area-box-web")

For more details, use --help on any command.
"""
    typer.echo(examples)


if __name__ == "__main__":
    # DEVELOPMENT MODE EXAMPLES (not for end users):
    # uv run src/web_llm_interactor/cli.py ask "What is the capital of Virginia?"
    # uv python -m web_llm_interactor.cli ask "What is the capital of Virginia?"
    # python -m web_llm_interactor.cli ask "What is the capital of Virginia?"
    #
    # INSTALLED USAGE (for end users):
    # web-llm-interactor ask "What is the capital of Virginia?"
    #
    # INSTALLATION:
    # uv pip install .  # Recommended

    app()
