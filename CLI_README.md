# Perplexity Stealth Agent CLI

A JavaScript CLI for AI agents to interact with Perplexity.ai using stealth automation.

## Features

- Send individual queries to Perplexity.ai
- Execute a sequence of tasks defined in a JSON file
- Use proxies (including BrightData) to avoid detection
- Save responses and screenshots
- Run security assessments on your codebase

## Installation

```bash
# Clone the repository
git clone [repository_url]
cd perplexity_spoof

# Install dependencies
npm install

# Make the CLI executable
chmod +x cli.js
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```
# BrightData configuration
BRIGHT_DATA_API_KEY=your_api_key_here
BRD_CUSTOMER_ID=your_customer_id
```

## Usage

### Basic Query

```bash
# Basic query with default settings
node cli.js query "What is quantum computing?"

# With headless mode
node cli.js query "What is quantum computing?" --headless

# With custom output directory
node cli.js query "What is quantum computing?" --output-dir=./my_responses
```

### Using BrightData Proxy

```bash
# Using BrightData proxy (requires BRIGHT_DATA_API_KEY and BRD_CUSTOMER_ID in .env)
node cli.js query "What is quantum computing?" --proxy=brightdata

# You can also set BRD_CUSTOMER_ID as an environment variable for a single command
export BRD_CUSTOMER_ID=your_customer_id
node cli.js query "What is quantum computing?" --proxy=brightdata
```

### Running Task Lists

```bash
# Execute a sequence of tasks from a JSON file
node cli.js tasks ./example-tasks.json

# With proxy and custom output directory
node cli.js tasks ./example-tasks.json --proxy=brightdata --output-dir=./task_responses
```

### Create a Task List Template

```bash
# Create a task list template
node cli.js create-tasks ./my-tasks.json
```

### Security Assessment

```bash
# Run a full security assessment
node cli.js security --full

# Analyze only the code
node cli.js security --code-only

# Check dependencies for vulnerabilities
node cli.js security --deps-only
```

## Task File Format

Task files should be in JSON format with the following structure:

```json
{
  "title": "Example Agent Task Workflow",
  "description": "A sequence of tasks demonstrating agent interaction with Perplexity.ai",
  "tasks": [
    {
      "title": "Basic Information Query",
      "prompt": "What is quantum computing?",
      "wait_time": 60000
    },
    {
      "title": "Another Task",
      "prompt": "Explain how neural networks work",
      "wait_time": 90000
    }
  ]
}
```

## Notes

- When using the BrightData proxy, set both `BRIGHT_DATA_API_KEY` and `BRD_CUSTOMER_ID` in your `.env` file
- For best results, use residential proxies to avoid detection
- The timeout parameter (`--wait-time`) controls how long to wait for responses
- Use headless mode (`--headless`) for production runs