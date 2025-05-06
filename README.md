# web_llm_interactor 🤖
A toolkit for automating interactions with web-based Large Language Models (LLMs) like Qwen, Perplexity, and more. This project leverages AppleScript to control a real Chrome browser (bypassing bot detection) and Python to extract structured responses from the resulting HTML.

## Why web_llm_interactor? 💡
Many cutting-edge LLMs are only accessible through browser-based interfaces, lacking public or affordable APIs. This restricts programmatic access for agents, scripts, or CLI workflows, unlike models with REST APIs.

web_llm_interactor solves this by enabling seamless interaction with web-based LLMs as if they had API endpoints. It automates browser actions using AppleScript to mimic human behavior, submits queries, waits for responses, and extracts structured data (e.g., JSON) from the page. This makes web-only LLMs fully compatible with your automation workflows.

## How It Works ⚙️
```
graph TD
    A[User/Agent calls CLI] --> B[AppleScript activates Chrome, finds correct tab]
    B --> C[AppleScript injects JavaScript to input query and submit]
    C --> D[AppleScript polls for LLM response to stabilize]
    D --> E[AppleScript saves page HTML to file]
    E --> F[Python parses HTML, extracts JSON]
    F --> G[Python outputs JSON with required fields]
    G --> H[CLI returns JSON to caller]
```

## Features ✨

- **Bypass Bot Detection**: Uses AppleScript to control a real Chrome browser, mimicking human interactions
- **Adaptive Response Polling**: Intelligently waits for responses by monitoring HTML length changes
- **Structured Output**: Extracts responses as JSON with customizable required fields
- **Automatic Form Submission**: Uses multiple strategies to send messages (form submit, button click, Enter key)
- **Multiple LLM Support**: Works with Qwen, Perplexity, and other browser-based LLMs
- **CLI Interface**: Simple command-line interface for easy integration
- **Focus Management**: Properly returns focus to your editor after processing
- **Customizable Fields**: Specify which fields must be present in extracted JSON

## Installation 🛠️

### Install with UV (Recommended)
```bash
# Clone the repository
git clone https://github.com/grahama1970/web-llm-interactor.git
cd web-llm-interactor

# Install with UV
uv pip install -e .

# Or use the installation script
./scripts/install_cpu_uv.sh
```

### Install with PIP
```bash
# Clone the repository
git clone https://github.com/grahama1970/web-llm-interactor.git
cd web-llm-interactor

# Install in development mode
pip install -e .
```

Requirements (managed by pyproject.toml):
- pyperclip
- python-dotenv
- loguru
- typer
- beautifulsoup4
- html2text
- bleach
- json-repair
- (MacOS with AppleScript support)

## Usage 🚀

### Command-Line Interface
```bash
# Basic usage with default settings (Qwen.ai)
web-llm-interactor ask "What is the capital of Georgia?"

# Specify a different LLM site
web-llm-interactor ask "What is the capital of France?" --url "https://chat.perplexity.ai/"

# Specify custom output HTML path
web-llm-interactor ask "What is the tallest mountain?" --output-html "./responses/mountain.html"

# Get all JSON objects, not just the last one
web-llm-interactor ask "List the largest oceans" --all

# Customize required JSON fields
web-llm-interactor ask "Explain quantum computing" --fields "question,answer"

# Skip adding JSON format instructions
web-llm-interactor ask "What's the weather in Tokyo?" --no-json-format

# Configure polling behavior
web-llm-interactor ask "What are the three branches of government?" --poll-interval 3 --stable-polls 2 --timeout 60
```

### Direct AppleScript Usage
```bash
# Basic usage
osascript src/web_llm_interactor/send_enter_save_source.applescript "What is the capital of Georgia?" "https://chat.qwen.ai/" "./output.html"

# Get all responses
osascript src/web_llm_interactor/send_enter_save_source.applescript "What is the capital of Florida?" "https://chat.qwen.ai/" "./output.html" "--all"

# Specify required fields
osascript src/web_llm_interactor/send_enter_save_source.applescript "Explain quantum computing" "https://chat.qwen.ai/" "./output.html" "--fields" "question,answer"
```

### Python Integration
```python
import subprocess
import json

def ask_web_llm(question, url="https://chat.qwen.ai/", custom_fields=None, get_all=False):
    """Query a web-based LLM and get a structured JSON response."""
    cmd = ["web-llm-interactor", "ask", question, "--url", url]
    
    if get_all:
        cmd.append("--all")
    
    if custom_fields:
        cmd.extend(["--fields", custom_fields])
    
    result = subprocess.check_output(cmd, text=True)
    return json.loads(result)

# Example usage
response = ask_web_llm("What is the capital of Idaho?")
print(f"Question: {response['question']}")
print(f"Answer: {response['answer']}")

# Get response with custom fields
custom_response = ask_web_llm(
    "Explain quantum computing in simple terms",
    custom_fields="question,answer"
)
print(custom_response["answer"])
```

## Why AppleScript Instead of Selenium? 🛡️

- **Stealth**: AppleScript controls a real Chrome browser, making interactions indistinguishable from a human user
- **Reliability**: Unlike Selenium, which is often detected via browser fingerprinting or navigator.webdriver, this approach works with sites that block bots
- **Simplicity**: No need for complex browser drivers or additional configurations

## How Polling Works

The system uses a simple but effective approach to detect when an LLM has finished responding:

1. Record the initial HTML length when the message is sent
2. Poll the page at regular intervals (configurable with `--poll-interval`)
3. When HTML grows significantly from initial state (>500 characters), start tracking stability
4. When HTML length stays the same for N consecutive polls (configurable with `--stable-polls`), consider the response complete
5. If maximum wait time is reached (configurable with `--timeout`), proceed with current content

This approach is more efficient than fixed wait times and works across different LLM interfaces.

## Project Structure 📂
```
web_llm_interactor/
├── src/
│   └── web_llm_interactor/
│       ├── __init__.py
│       ├── cli.py                        # Command-line interface
│       ├── send_enter_save_source.applescript  # Browser automation script
│       ├── extract_json_from_html.py     # HTML-to-JSON extractor
│       ├── file_utils.py                 # File handling utilities
│       └── json_utils.py                 # JSON parsing utilities
├── scripts/
│   ├── demo.sh                           # Demo script showing usage examples
│   └── cleanup.sh                        # Script to clean up temporary files
├── README.md
└── pyproject.toml
```

## Troubleshooting 🔍

- **No Chrome Tab Found**: Make sure you have Chrome open with the correct URL (e.g., https://chat.qwen.ai/)
- **Empty Response**: Try increasing the timeout with `--timeout 60`
- **JSON Extraction Failed**: Ensure the LLM is responding with properly formatted JSON or specify required fields with `--fields`
- **Response Too Slow**: Adjust polling parameters with `--poll-interval` and `--stable-polls`

## License 📜
MIT License

---

web_llm_interactor empowers agents and CLI workflows to harness web-only LLMs, delivering API-like functionality with minimal setup. 🌟