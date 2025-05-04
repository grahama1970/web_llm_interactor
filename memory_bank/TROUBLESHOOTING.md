# Troubleshooting Guide

This document provides guidance on common issues and their resolutions encountered within the project.

## ArangoDB Connection Issues

*   **Problem:** Cannot connect to ArangoDB instance.
*   **Solution:**
    1.  Verify the ArangoDB Docker container is running (`docker ps`).
    2.  Check the `ARANGO_HOST`, `ARANGO_USER`, `ARANGO_PASSWORD`, `ARANGO_DB_NAME` environment variables are correctly set and exported.
    3.  Ensure the host specified in `ARANGO_HOST` is reachable from where the script is being run.

## Embedding Generation Failures

*   **Problem:** Errors related to OpenAI API key or embedding model.
*   **Solution:**
    1.  Verify `OPENAI_API_KEY` environment variable is set correctly.
    2.  Check the specified embedding model name in `config.py` (`EMBEDDING_MODEL`) is valid and accessible via the API key.
    3.  Ensure network connectivity to the OpenAI API endpoint.

## AQL Query Errors

*   **Problem:** `ArangoServerError` or `AQLQueryExecuteError` during database operations.
*   **Solution:**
    1.  Examine the AQL query logged by the function causing the error.
    2.  Check for syntax errors in the AQL query.
    3.  Verify that the collections, views, and analyzers referenced in the query exist and are correctly configured (use `setup_arangodb.py` if needed).
    4.  Ensure bind variables (`@variable`) used in the query are correctly provided when executing the query.
  
  ## Typer CLI Pattern Problems and Solutions
  
  ### Common Typer Configuration Issues
  
  1. **Incorrect Entry Point Pattern (Most Common)**
     * **Problem Signs:**
       - "Got unexpected extra argument" errors
       - Arguments not being parsed correctly
       - Subcommands not working as expected
     * **Root Causes:**
       - Using a wrapper function instead of direct app reference
       - Legacy Python CLI patterns influence (e.g., argparse-style main())
       - Click documentation carrying over incorrect patterns
     * **Correct Pattern:**
       ```python
       # cli.py
       app = typer.Typer()  # Module-level app instance
       
       @app.command()  # Direct decoration, no function wrapper
       def process(...):  # Command logic here
           ...
       
       if __name__ == "__main__":
           app()  # Only call app() in __main__
       ```
     * **Wrong Pattern (AVOID):**
       ```python
       # WRONG - Don't do this!
       def main():
           app()  # Wrapper breaks argument parsing
       
       if __name__ == "__main__":
           main()  # Extra layer causes issues
       ```
  
  2. **Entry Point Configuration**
     * In `pyproject.toml`:
       ```toml
       [project.scripts]
       my-cli = "package.cli:app"  # Point to app object
       # WRONG: my-cli = "package.cli:main"  # Never point to a wrapper
       ```
  
  3. **Command Organization**
     * **Single Command:** Use unnamed decorator
       ```python
       @app.command()  # No name needed
       def process(): ...
       ```
     * **Multiple Commands:** Name each explicitly
       ```python
       @app.command("search")
       def search_cmd(): ...
       
       @app.command("index")
       def index_cmd(): ...
       ```
  
  4. **Prevention Strategy**
     * Always use direct app object in entry points
     * Keep app() calls only in __main__ blocks
     * Remove all wrapper functions
     * Use explicit command names for multi-command CLIs
     * Test with --help to verify command structure
  
  ### Legacy Code Migration
  
  When converting old CLI code to Typer:
  1. Remove any main() wrapper functions
  2. Convert argparse/click patterns to @app.command decorators
  3. Update entry points to point to app object
  4. Test command structure with --help
  5. Verify argument parsing with sample inputs
  
  ## Previous Entry Point Configuration Section

*   **Problem:** CLI subcommands fail with `Got unexpected extra argument` when using entry points defined in `pyproject.toml`.
*   **Root Cause:** The entry point points to a wrapper function that calls the Typer app (`app()`) instead of pointing directly to the app object.
*   **Solution:**
    1.  In `pyproject.toml`, point the entry point directly to the Typer app object:
        ```toml
        [project.scripts]
        my-cli = "my_package.cli:app"  # Point to the app object
        ```
    2.  In the CLI module:
        ```python
        app = typer.Typer()
        @app.command()
        def my_command(): ...
        
        if __name__ == "__main__":
            app()  # Only call app() in __main__
        ```
    3.  Do NOT use a wrapper function like:
        ```python
        # WRONG:
        def main():
            app()  # This breaks subcommand dispatch
        ```

## CLI Command Execution

*   **Problem:** Running CLI commands fails or produces unexpected errors.
*   **Solution:**
    1.  **Execution Pattern:** Always execute CLI commands using the `uv run python -m <module_path> ...` pattern from the project root directory.
        *   Example: `uv run python -m src.complexity.arangodb.cli search bm25 "query terms"`
    2.  **Environment:** Ensure all required environment variables (ArangoDB connection details, API keys) are loaded into the environment where `uv run` is executed.
    3.  **Arguments:** Double-check the command, subcommand, arguments, and options against the command's help text (`uv run python -m <module_path> [COMMAND] [SUBCOMMAND] --help`). Pay attention to required arguments vs. options.
    4.  **File Paths:** Ensure any file paths provided via options like `--data-file` are correct relative to the project root or absolute paths.
    5.  **JSON Data:** When providing data via `--data` option, ensure the JSON string is valid and properly escaped for the shell. Using `--data-file` is generally safer.
    6.  **Dependencies:** Make sure project dependencies are installed correctly (`uv sync`).

*(Add more sections as new troubleshooting steps are identified)*