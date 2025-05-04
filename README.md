# Perplexity.ai Stealth Automation with MCP Desktop Commander

This project automates interaction with Perplexity.ai by entering a prompt into the chat window using Playwright with stealth techniques to avoid detection. It incorporates Bézier spline mouse movements for human-like behavior and manual fingerprint spoofing to evade browser fingerprinting.

The automation leverages MCP SuperAssistant and Desktop Commander to interact with local files for enhanced capabilities. This enables the script to prompt Perplexity's AI to access and read local files through the Desktop Commander tool.

## Features

- **MCP Integration**: Uses MCP SuperAssistant Chrome plugin to access the desktop-commander tool
- **Fully Configurable**: Edit settings in `src/config.js` or use command-line options
- **BrightData Integration**: Built-in support for BrightData residential proxies with API key
- **Advanced Stealth**: Multiple techniques to bypass bot detection:
  - Stealth plugin to bypass anti-bot detection
  - Fingerprint spoofing via JavaScript injection (canvas, WebGL, navigator)
  - Random User-Agent generation
  - Human-like mouse movements using Bézier splines
  - Variable typing speed
  - Random pre-interaction movements
- **Response Capture**: Automatically captures and saves responses
- **Debugging**: Screenshot capture at each step
- **Modern Structure**: Organized into a standard src-based JavaScript project

## Prerequisites

- **Node.js**: Version 14 or higher (download from [nodejs.org](https://nodejs.org/))
- **Google Chrome**: Installed for non-headless mode (recommended)
- **MCP SuperAssistant**: Chrome extension for accessing desktop-commander ([Install from Chrome Web Store](https://chromewebstore.google.com/detail/mcp-superassistant/kngiafgkdnlkgmefdafaibkibegkcaef))
- **Desktop Commander**: Local tool for file system access ([Desktop Commander App](https://desktopcommander.app/))

## Installation

### Clone the Repository

```bash
git clone <repository-url>
cd perplexity-stealth-automation
```

Alternatively, create a directory and add the provided files.

### Install Dependencies

```bash
npm install
```

This installs playwright, playwright-extra, puppeteer-extra-plugin-stealth, user-agents, and dotenv.

### Install Playwright Browsers

```bash
npx playwright install
```

This step is crucial, as Playwright does not include browser binaries in the npm package. The command may take a few minutes and requires ~500MB of disk space.

### Setup MCP SuperAssistant

1. Install the MCP SuperAssistant Chrome extension from the [Chrome Web Store](https://chromewebstore.google.com/detail/mcp-superassistant/kngiafgkdnlkgmefdafaibkibegkcaef)

2. Install and run Desktop Commander using npx:

```bash
npx @anthropic-ai/desktop-commander@latest
```

This will start the Desktop Commander service, which allows controlled access to local files.

3. After installation, authorize MCP SuperAssistant in your Chrome browser to enable seamless interaction with local files via Perplexity.ai prompts.

## Configuration

All settings can be configured in `src/config.js`. The main configuration options are:

- **Prompt**: The text to enter into Perplexity.ai (includes MCP commands)
- **Browser**: Headless mode, viewport size, locale, and geolocation
- **Proxy**: Proxy settings (none, custom, BrightData)
- **Timing**: Delays for typing, mouse movements, and waiting for response
- **Mouse Movement**: Control randomness and steps in Bézier curves
- **Debug**: Screenshot capture and logging options

### MCP Desktop Commander Integration

The default prompt in the configuration is set to use the MCP Desktop Commander tool to read local files. You can modify the prompt in `src/config.js` to specify different files or change the commands.

Example prompt:
```
Use the local MCP tool desktop-commander to read the file located at ~/Downloads/Arc_Prize_Guide.txt. Return the file's contents. Do not use any other method. Then create a concise summary of the text file
```

Make sure Desktop Commander is running (via `npx @anthropic-ai/desktop-commander@latest`) before starting the automation for the MCP commands to work properly.

## Usage

> **IMPORTANT**: Before running any command, make sure you have Desktop Commander running with `npx @anthropic-ai/desktop-commander@latest` in a separate terminal window.

### Basic Usage

```bash
npm start
```

This runs the script with default settings, which includes using the MCP Desktop Commander prompt.

### With BrightData API Key (.env)

```bash
# First, start Desktop Commander if not already running
npx @anthropic-ai/desktop-commander@latest

# Then in a separate terminal, run with BrightData proxy (uses API key from .env)
npm run brightdata

# Run with BrightData proxy in headless mode
npm run brightdata:headless

# Run with BrightData proxy with a custom prompt
npm run brightdata "Use the local MCP tool desktop-commander to read the file located at ~/Desktop/example.txt. Return the file's contents."
```

### With Command-line Runner

```bash
# Basic run with default config
npm run run

# Run in headless mode
npm run run -- --headless

# Use BrightData proxy with interactive setup
npm run run -- --proxy=brightdata -i
# or use the shorthand
npm run proxy:brightdata

# Specify a custom prompt
npm run run -- --prompt="What is the capital of France?"

# Use a custom config file
npm run run -- --config=./my-config.js

# Get help
npm run run -- --help
```

## Python CLI for AI Agents

This project includes a Python CLI specifically designed for AI agents to interact with Perplexity.ai through a structured interface. The CLI is located in the `python_cli` directory.

### Features

- Execute individual queries or batches of tasks
- Process responses in a structured way
- Configure proxy settings, timeouts, and output paths
- Built with Typer for excellent command-line experience

### Installation

```bash
cd python_cli
pip install -r requirements.txt
```

### Usage Examples

```bash
# Send a single query
./perplexity_cli.py query "What is quantum computing?"

# Execute a list of tasks from a JSON file
./perplexity_cli.py tasks example_tasks.json --headless --proxy brightdata

# Create a template task list
./perplexity_cli.py create-tasks my-tasks.json

# Run a security assessment
./perplexity_cli.py security --full
```

For full documentation and examples, see the [Python CLI README](./python_cli/README.md).

### Environment Variables

You can set these environment variables to configure BrightData:

- `BRIGHT_DATA_API_KEY`: Your BrightData API key (recommended)
- `BRD_CUSTOMER_ID`: Your BrightData customer ID
- `BRD_PASSWORD`: Your BrightData password (alternative to API key)

Create a `.env` file in the project root with your BrightData credentials:

```
BRIGHT_DATA_API_KEY=your_api_key_here
BRD_CUSTOMER_ID=your_customer_id_here
```

## Advanced Features

### Custom Proxy Configuration

Edit the `config.js` file to configure custom proxies:

```javascript
proxy: {
  enabled: true,
  type: 'custom',
  custom: {
    server: 'http://proxy.example.com:8080',
    username: 'user',
    password: 'pass'
  }
}
```

### BrightData Proxy Configuration

```javascript
proxy: {
  enabled: true,
  type: 'brightdata',
  brightdata: {
    server: 'http://brd.superproxy.io:22225',
    username: 'brd-customer-YOUR_CUSTOMER_ID-zone-residential',
    password: 'YOUR_PASSWORD',
    zone: 'residential'
  }
}
```

## Security Evaluation

The project includes two methods for security evaluation:

1. An automated security evaluation tool based on the Hacker methodology
2. A Claude AI-powered security analysis using a specialized Hacker system prompt

### Automated Security Evaluation

```bash
# Using npm scripts (recommended)
npm run security          # Run a full security assessment
npm run security:deps     # Only check dependencies
npm run security:code     # Only analyze code

# Or run directly with more options
node security-eval.js --full
node security-eval.js --check-deps
node security-eval.js --analyze-code
node security-eval.js --output=./my-report.md
```

The tool will generate a detailed security report that includes:
- Vulnerability assessment of dependencies
- Code analysis for security issues
- Recommendations for security improvements
- OWASP Top 10 categorization of issues

### Claude Hacker Mode

For a more comprehensive security analysis, you can use Claude with a specialized Hacker system prompt that focuses on identifying security vulnerabilities:

```bash
# Make sure you have Claude CLI installed first
npm install -g @anthropic-ai/claude-cli

# Run the Claude Hacker analysis using npm script
npm run security:claude

# Or run directly
./run-claude-hacker.sh
```

This will run Claude with a security-focused system prompt to:
- Identify potential attack surfaces in the code
- Formulate exploit strategies
- Provide detailed security recommendations
- Classify vulnerabilities according to industry standards

### Security Best Practices

When using this tool, always follow these security best practices:
- Never store API keys or credentials directly in the code
- Use environment variables for sensitive information
- Keep all dependencies updated to their latest versions
- Run security evaluations regularly to catch new issues
- Follow the recommendations provided in security reports

#### Environment Variables and Sensitive Data

This project uses example files for environment variables and configuration:

- `.env.example` - A template showing required environment variables
- `.mcp.json.example` - A template for MCP configuration

To set up your environment:

1. Copy `.env.example` to `.env` and add your actual credentials
2. Copy `.mcp.json.example` to `.mcp.json` and add your actual API keys

**IMPORTANT**: Never commit your `.env` or `.mcp.json` files to version control. They are included in `.gitignore` to prevent accidental exposure of credentials.

## Troubleshooting

### MCP Desktop Commander Issues

If the MCP commands are not working:

- Make sure Desktop Commander is running with `npx @anthropic-ai/desktop-commander@latest`
- Verify that the MCP SuperAssistant Chrome extension is installed and authorized
- Check that the file paths in your prompts are correct and accessible
- If needed, restart the Desktop Commander service
- Try running Desktop Commander with admin privileges if file access is denied

### Timeout Error (page.goto)

If you see Timeout 60000ms exceeded during navigation:

- Check your internet connection
- Use a residential proxy to bypass IP-based anti-bot measures
- Increase the timeout in src/config.js
- Test with headless: true to rule out non-headless issues
- Check for CAPTCHA detection messages

### Prompt Not Entered

If the script fails to enter the prompt:

- Check the console output for error messages
- Verify that the input selectors match Perplexity.ai's current DOM
- Ensure the page loads fully (no CAPTCHA or anti-bot page)
- Increase the input field wait timeout in src/config.js

### CAPTCHA or Anti-Bot Detection

If a CAPTCHA or verification page appears:

- Use a residential proxy (BrightData recommended)
- Test with the included fingerprint spoofing
- Check for CAPTCHA detection in the logs
- Consider trying different User-Agent configurations

### Browser Binary Missing Error

If Playwright browsers are missing:

```bash
npx playwright install
```

## Ethical Considerations

- Use this script only for authorized cybersecurity research or testing
- Obtain permission before interacting with Perplexity.ai
- Avoid overloading servers or violating terms of service
- Comply with applicable laws (e.g., CFAA in the U.S.)

## License

MIT License