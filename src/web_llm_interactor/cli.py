"""
web-llm-interactor: Interact with web-based LLMs (like Qwen, Perplexity, etc.) from the command line or agent scripts.

Send a message to a web chat LLM, extract the structured JSON response, and use it in your agent or workflow.

Examples:
  web-llm-interactor ask "What is the capital of Georgia?"
  web-llm-interactor ask "Who is the CEO of Apple?" --url "https://chat.perplexity.ai/" --output-html "./perplexity_response.html"
  web-llm-interactor ask "What is the capital of Florida?" --all

Use --help on any command for more details.
"""

import typer
import subprocess
import time
from pathlib import Path
from web_llm_interactor.file_utils import generate_html_filename

app = typer.Typer(
    help="""
web-llm-interactor: Interact with web-based LLMs (like Qwen, Perplexity, etc.) from the command line or agent scripts.

Send a message to a web chat LLM, extract the structured JSON response, and use it in your agent or workflow.

Examples:
  web-llm-interactor ask "What is the capital of Georgia?"
  web-llm-interactor ask "Who is the CEO of Apple?" --url "https://chat.perplexity.ai/" --output-html "./perplexity_response.html"
  web-llm-interactor ask "What is the capital of Florida?" --all
"""
)

DEFAULT_SCRIPT_PATH = Path("src/send_enter_save_source.applescript").resolve()
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
):
    """
    Send a message to a web LLM chat page and extract the JSON response.
    """
    # Generate a unique filename if not provided
    if output_html is None:
        output_html = generate_html_filename(question, url)
        typer.echo(f"Saving HTML to: {output_html}")

    typer.echo(f"Sending: {question}")
    for attempt in range(max_attempts):
        try:
            args = [
                "osascript",
                str(script_path),
                question,
                url,
                str(output_html),
            ]
            if all:
                args.append("--all")
            result = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True,
                timeout=timeout,
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

Arguments:
  question           The question or message to send to the LLM.

Options:
  --url, -u          The target chat URL (default: https://chat.qwen.ai/)
  --output-html, -o  Path to save the output HTML file (default: ./output.html)
  --all              Return all JSON objects, not just the last one.
  --applescript      Path to the AppleScript file to use.
  --max-attempts     Maximum retry attempts for response (default: 3)
  --timeout          Timeout per attempt in seconds (default: 30)

For more details, use --help on any command.
"""
    typer.echo(examples)


if __name__ == "__main__":
    app()
