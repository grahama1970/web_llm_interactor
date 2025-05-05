# LLM Summarizer Integration Strategy

This document outlines strategies for integrating the functionality provided by the `llm-summarizer` project into other projects, such as `pdf_extractor`.

## Available Interfaces

The `llm-summarizer` offers two primary interfaces:

1.  **Command-Line Interface (CLI):**
    *   Defined in `src/summarizer/cli.py`.
    *   Accessible via the `summarizer-cli` entry point (if installed) or `uv run python -m summarizer.cli summarize ...`.
    *   Provides a direct way to invoke summarization from the command line or shell scripts.
    *   See `src/summarizer/cli_summary.md` for detailed usage.

2.  **FastAPI Application (API):**
    *   Defined in `src/summarizer/api.py`.
    *   Provides an HTTP-based interface (currently via a `/summarize` endpoint) mirroring the CLI's functionality.
    *   Can be run as a standalone service using `uvicorn` (e.g., `uv run python src/summarizer/api.py` or `uvicorn summarizer.api:app --reload --port 8001`).
    *   Intended as an option for service-oriented integration or as a foundation for a future Model Context Protocol (MCP) server.

## Integration Options for Local Development (e.g., with `pdf_extractor`)

When integrating `llm-summarizer` with another local project like `pdf_extractor` during development, consider these options:

1.  **Local Editable Install (Recommended):**
    *   **How:** Within the `pdf_extractor` project's virtual environment, run `uv pip install -e /path/to/llm-summarizer`.
    *   **Pros:**
        *   Treats `llm-summarizer` as a standard Python package within `pdf_extractor`.
        *   Allows direct import of `llm-summarizer` functions (e.g., `from summarizer.text_summarizer import summarize_text`) within `pdf_extractor` code.
        *   Avoids code duplication.
        *   Changes made to `llm-summarizer` code are immediately reflected when running `pdf_extractor`.
        *   Simplifies debugging across both projects.
        *   Relatively simple setup.
    *   **Cons:**
        *   Couples the development environments; requires both projects to be present locally.

2.  **Git Submodule:**
    *   **How:** Add `llm-summarizer` as a Git submodule within the `pdf_extractor` repository (`git submodule add <repo_url> path/to/submodule`). The `llm-summarizer` code could then potentially be added to `pdf_extractor`'s `PYTHONPATH` or installed similarly to an editable install from the submodule path.
    *   **Pros:**
        *   Keeps `llm-summarizer`'s Git history separate but linked.
        *   Makes pulling updates from the `llm-summarizer` repository explicit.
    *   **Cons:**
        *   Adds complexity to the Git workflow (initializing, updating, cloning submodules).
        *   Still requires careful management of how the submodule code is made available to the parent project's Python environment.

3.  **FastAPI Service Interaction:**
    *   **How:** Run the `llm-summarizer` FastAPI application (`src/summarizer/api.py`) as a separate process. Modify `pdf_extractor` to make HTTP requests (e.g., using `requests` or `httpx`) to the `/summarize` endpoint of the running API service.
    *   **Pros:**
        *   Strong decoupling; `pdf_extractor` only needs the API endpoint URL and request/response schema.
        *   Allows `llm-summarizer` to run independently.
    *   **Cons:**
        *   Higher overhead for local development (running two services, implementing HTTP clients, handling network communication).
        *   Less direct debugging experience compared to direct imports.

## Future MCP Integration

The FastAPI application (`src/summarizer/api.py`) serves as a potential foundation for creating an MCP server for `llm-summarizer`.

*   The existing `/summarize` endpoint could be exposed as an MCP tool.
*   The FastAPI application could be containerized (e.g., using Docker) and configured to run as an MCP server (stdio-based or SSE-based).
*   This would allow other MCP-enabled applications (like a future version of `pdf_extractor` or an orchestrator agent) to discover and use the summarization functionality via the standardized MCP `use_mcp_tool` calls, rather than direct code imports or custom HTTP requests.

## Summary Recommendation

*   For **current local development and integration** between `llm-summarizer` and `pdf_extractor`, the **Local Editable Install** is the recommended approach due to its simplicity and efficiency.
*   The **FastAPI application (`api.py`)** exists as a parallel interface, providing an option for **future service-oriented integration** or **development into an MCP server**.
*   **Git Submodules** offer an alternative for repository management but add workflow complexity.
*   **Copy/Pasting code** should be avoided due to maintainability issues.