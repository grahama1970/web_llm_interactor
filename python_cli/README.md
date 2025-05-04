# Perplexity Stealth Agent CLI

A Python CLI wrapper for the Perplexity Stealth Automation JavaScript project. This CLI is specifically designed for AI agents to interact with Perplexity.ai through a structured interface.

## Features

- **Single Query Mode**: Send individual prompts to Perplexity.ai
- **Task List Mode**: Execute a sequence of tasks defined in a JSON file
- **Security Assessment**: Run security evaluations on the codebase
- **Rich Output**: Clear, formatted console output with progress indicators
- **Proxy Support**: Configure BrightData or custom proxies

## Installation

1. Make sure you have Python 3.8+ installed
2. Install the required dependencies:

```bash
cd python_cli
pip install -r requirements.txt
```

3. Ensure the parent JavaScript project is properly set up:
   - Install Node.js dependencies (`npm install` in the project root)
   - Set up any required environment variables in `.env`

## Usage

### Basic Query

To send a single query to Perplexity.ai:

```bash
python perplexity_cli.py query "What is the capital of France?"
```

With options:

```bash
python perplexity_cli.py query "What is the capital of France?" --headless --proxy brightdata --output-dir ./my-responses
```

### Executing Task Lists

Define a list of tasks in a JSON file:

```bash
# Create a template tasks file
python perplexity_cli.py create-tasks ./my-tasks.json

# Edit the file with your task definitions

# Execute the tasks
python perplexity_cli.py tasks ./my-tasks.json --headless --proxy brightdata
```

Task file format:

```json
{
  "title": "Example Task List",
  "description": "A list of tasks to execute on Perplexity.ai",
  "tasks": [
    {
      "title": "Basic Query",
      "prompt": "What is the capital of France?",
      "wait_time": 60000
    },
    {
      "title": "Desktop Commander Example",
      "prompt": "Use the local MCP tool desktop-commander to read the file located at ~/Downloads/example.txt. Return the file's contents. Then summarize it.",
      "wait_time": 90000
    }
  ]
}
```

### Security Assessment

Run a security assessment on the codebase:

```bash
python perplexity_cli.py security --full --output ./my-security-report.md
```

## For AI Agents

This CLI is designed to be used by AI agents that need to:

1. Execute sequential tasks on Perplexity.ai
2. Process responses in a structured way
3. Access local files through MCP Desktop Commander
4. Maintain state between tasks

Each task's output is saved in a dedicated directory, making it easy for agents to parse and reference previous results.

## Environment Variables

The CLI uses the same environment variables as the JavaScript project:

- `BRIGHT_DATA_API_KEY`: Your BrightData API key
- `BRD_CUSTOMER_ID`: Your BrightData customer ID

These can be set in a `.env` file in the project root.

## Error Handling

The CLI provides robust error handling:

- Command execution errors are properly captured and reported
- Progress indicators show the current state of execution
- Task results include success/failure status
- Each task has isolated output directories