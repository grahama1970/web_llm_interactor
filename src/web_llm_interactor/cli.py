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
):
    """
    Send a message to a web LLM chat page and extract the JSON response.
    """
    # Generate a unique filename if not provided
    if output_html is None:
        output_html = generate_html_filename(question, url)
        typer.echo(f"Saving HTML to: {output_html}")

    typer.echo(f"Sending: {question}")
    args = [
        "osascript",
        str(script_path),
        question,
        url,
        str(output_html),
    ]
    if all:
        args.append("--all")
    try:
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        typer.echo("Result from web LLM:")
        typer.echo(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        typer.secho("AppleScript Error:", fg=typer.colors.RED, err=True)
        typer.secho(e.stderr.strip(), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


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

For more details, use --help on any command.
"""
    typer.echo(examples)


if __name__ == "__main__":
    app()
