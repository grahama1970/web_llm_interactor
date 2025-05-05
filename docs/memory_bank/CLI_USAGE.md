# Summarizer CLI Usage

This document describes how to use the command-line interface (CLI) for the `llm-summarizer`.

## Overview

The CLI allows you to summarize text provided directly, from a file, or from a Wikipedia article. It uses the core summarization logic, including handling long text via MapReduce chunking and configurable embedding models for validation (though validation isn't directly exposed via the CLI currently).

## Prerequisites

- Ensure project dependencies are installed: `uv sync`
- Set environment variables if using OpenAI embeddings: `export OPENAI_API_KEY='your-key'`

## Running the CLI

The CLI can be run either after installation or directly from the source:

### After Installation
```sh
# After pip/uv install
summarizer-cli [OPTIONS]
```

### During Development
```sh
# Direct execution (development)
env PYTHONPATH=src uv run python -m summarizer.cli [OPTIONS]
```

## Important Usage Notes

**Recommended Invocation Pattern:**
Always use the installed command or the module execution pattern. Both work identically:

```sh
# After installation:
summarizer-cli --file input.txt --output summary.txt

# During development:
env PYTHONPATH=src uv run python -m summarizer.cli --file input.txt --output summary.txt
```

**Recommendation:**

To avoid issues with direct text input, **always use the `--file <path>` option**. For small text snippets, write the text to a temporary file first and then provide the path to that file using `--file`. This method is reliable for both small and large inputs.
## Commands

### `summarize`

Summarizes the provided input.

**Arguments:**

*   `[TEXT]`: (Optional) Text to summarize provided directly as an argument.

**Options:**

*   `--file, -f PATH`: Path to a text file to summarize.
*   `--wiki, -w TEXT`: Wikipedia article title to summarize.
*   `--max-wiki-tokens INTEGER`: Maximum tokens to load from Wikipedia article. [default: 6000]
*   `--output, -o PATH`: Path to save the summary file. If omitted, prints to standard output.
*   `--model TEXT`: LLM model to use for summarization. [default: gpt-4o-mini]
*   `--temperature FLOAT`: LLM temperature. [default: 0.7]
*   `--context-limit INTEGER`: Approximate context token limit before chunking. [default: 3800]
*   `--chunk-size INTEGER`: Target token size for chunks. [default: 3500]
*   `--overlap INTEGER`: Number of sentences to overlap between chunks. [default: 2]
*   `--embedding-provider TEXT`: Embedding provider ('local' or 'openai'). [default: local]
*   `--local-embedding-model TEXT`: Name of local sentence-transformer model. [default: nomic-ai/modernbert-embed-base]
*   `--openai-embedding-model TEXT`: Name of OpenAI embedding model. [default: text-embedding-ada-002]
*   `--log-level TEXT`: Set log level (e.g., DEBUG, INFO, WARNING). [default: INFO]
*   `--help`: Show help message and exit.

## Examples

**1. Summarize direct text:**

```sh
# Note: Direct text argument is unreliable with uv run. Use --file instead.
# Example using --file (recommended):
# echo "Artificial intelligence (AI)..." > temp_ai.txt
# env PYTHONPATH=src uv run python -m summarizer.cli summarize --file temp_ai.txt
# rm temp_ai.txt
#
# Original example (may fail with uv run):
# uv run python src/summarizer/cli.py "Artificial intelligence (AI)..."
env PYTHONPATH=src uv run python -m summarizer.cli summarize --file test_input.txt # Using a pre-made file for example
```

**2. Summarize text from a file:**

```sh
env PYTHONPATH=src uv run python -m summarizer.cli summarize --file ./path/to/your/document.txt
```

**3. Summarize a Wikipedia article:**

```sh
env PYTHONPATH=src uv run python -m summarizer.cli summarize --wiki "Machine Learning"
```

**4. Summarize a long Wikipedia article and save to file:**

```sh
env PYTHONPATH=src uv run python -m summarizer.cli summarize --wiki "World War II" --max-wiki-tokens 10000 --output ./summary_ww2.txt
```

**5. Summarize using a different model and higher temperature:**

```sh
env PYTHONPATH=src uv run python -m summarizer.cli summarize --file input.txt --model gpt-4-turbo --temperature 0.9
```

**6. Summarize using OpenAI embeddings (requires OPENAI_API_KEY env var):**

```sh
# Make sure OPENAI_API_KEY is set
env PYTHONPATH=src uv run python -m summarizer.cli summarize --wiki "Python (programming language)" --embedding-provider openai --openai-embedding-model text-embedding-3-small
```

**7. Enable DEBUG logging:**

```sh
env PYTHONPATH=src uv run python -m summarizer.cli summarize --file input.txt --log-level DEBUG
---

## Entry Point Configuration (CRITICAL)

**Required Structure:**

1. In `pyproject.toml`, point directly to the Typer app object:
   ```toml
   [project.scripts]
   summarizer-cli = "summarizer.cli:app"  # Point to the app object, NOT a wrapper function
   ```

2. In the CLI module (`cli.py`):
   ```python
   import typer
   
   app = typer.Typer()  # Create the app instance
   
   @app.command()
   def summarize(...):  # Define commands
       ...
   
   if __name__ == "__main__":
       app()  # Only call app() in __main__
   ```

**Common Pitfalls:**

1. **DO NOT** use a wrapper function as the entry point:
   ```toml
   # WRONG:
   summarizer-cli = "summarizer.cli:main"  # Points to a function that calls app()
   ```

2. **DO NOT** call `app()` at module level:
   ```python
   # WRONG:
   app = typer.Typer()
   @app.command()
   def summarize(): ...
   app()  # Don't call here!
   ```

3. **ALWAYS** let Typer handle argument parsing:
   - Entry point should point to the `app` object
   - All argument handling should be through Typer decorators
   - Never manually parse sys.argv

**Key Points:**
- Entry point MUST be the Typer app object itself
- Keep command logic in decorated functions
- Only call `app()` in `if __name__ == "__main__"`

---