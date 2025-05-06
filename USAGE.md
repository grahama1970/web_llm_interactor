# web-llm-interactor Usage Guide

This tool allows you to interact with web-based LLMs (like Qwen, Perplexity, etc.) from the command line or agent scripts.

## Prerequisites

- macOS (AppleScript is required)
- Google Chrome browser
- Python 3.8+

## Installation

```bash
# Install from source (using uv - recommended)
git clone https://github.com/yourusername/web-llm-interactor.git
cd web-llm-interactor
uv pip install .

# Or use the installation script
./scripts/install_cpu_uv.sh

# Or if published to PyPI
uv pip install web-llm-interactor
```

## Important: Open Chrome Before Running

**Before running any commands, you must open the target LLM website in Chrome:**

1. Open Google Chrome
2. Navigate to your preferred LLM website (default is https://chat.qwen.ai/)
3. Make sure you're logged in if required

## Basic Usage

```bash
# Basic usage (uses Qwen by default)
web-llm-interactor ask "What is the capital of France?"

# Use a different LLM website
web-llm-interactor ask "What is the capital of Japan?" --url "https://chat.perplexity.ai/"

# Save HTML output to a specific location
web-llm-interactor ask "What is the population of Brazil?" --output-html "./my_response.html"

# Get all JSON objects from the response, not just the last one
web-llm-interactor ask "List the planets in order from the sun" --all

# Specify required fields in the JSON response
web-llm-interactor ask "Explain quantum computing" --fields "question,answer"

# Don't append JSON format instructions to the query
web-llm-interactor ask "What's the weather like in Paris?" --no-json-format
```

## Advanced Options

- `--timeout` - Set timeout per attempt in seconds (default: 30)
- `--max-attempts` - Set maximum retry attempts (default: 3)
- `--poll-interval` - Set interval between response polls in seconds (default: 2)
- `--stable-polls` - Set number of stable polls required to consider response complete (default: 3)
- `--selector` - Specify CSS selector for the chat input field

## Troubleshooting

If you encounter errors:

1. **"No Chrome tab found with URL..."** - Make sure you have Chrome open with the specified URL
2. **"Empty response received"** - Try increasing the timeout with `--timeout`
3. **"Page HTML was empty"** - Check if the LLM website is loading properly

## For Developers

If you're working on the code itself, you can run it directly with:

```bash
# Development mode examples
python -m web_llm_interactor.cli ask "Your question"
uv run src/web_llm_interactor/cli.py ask "Your question"
```

## Common Examples

```bash
web-llm-interactor ask "What is the capital of Georgia?"
web-llm-interactor ask "Who is the CEO of Apple?" --url "https://chat.perplexity.ai/" --output-html "./perplexity_response.html"
web-llm-interactor ask "What is the capital of Florida?" --all
web-llm-interactor ask "Explain quantum computing" --fields "question,answer"
web-llm-interactor ask "What's the weather like in Paris?" --no-json-format
web-llm-interactor ask "List the planets in our solar system" --timeout 45
web-llm-interactor ask "How does photosynthesis work?" --selector "textarea.chat-input"
```