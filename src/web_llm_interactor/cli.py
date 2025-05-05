# src/cli.py
import typer
import subprocess
from pathlib import Path

app = typer.Typer()

SCRIPT_PATH = Path("src/send_enter_save_source.applescript").resolve()
PYTHON_BIN = Path(".venv/bin/python").resolve()


@app.command()
def ask(question: str):
    """
    Send a message to Qwen and extract the final JSON.
    """
    print(f"Sending: {question}")
    try:
        result = subprocess.run(
            ["osascript", str(SCRIPT_PATH), question],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        print("Result from Qwen:")
        print(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print("AppleScript Error:")
        print(e.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
