# Qwen AI Chat Automation with Vision Support

This module provides automation support for interacting with https://chat.qwen.ai/ using the Qwen-VL (Vision-Language) model for intelligent UI detection and interaction.

## Overview

The Qwen implementation uses vision-based automation to:

1. Detect UI elements in the chat.qwen.ai interface
2. Send queries and extract responses
3. Handle CAPTCHAs and other verification challenges
4. Work across different screen resolutions and UI themes

## Requirements

In addition to the base requirements, you'll need:

```bash
# Install dependencies
pip install -r requirements_qwen.txt
```

The key dependencies include:
- PyTorch
- Transformers
- PIL
- pyautogui
- pyperclip

## Usage

```bash
# Basic usage
python qwen_main.py --query "What are the latest advancements in quantum computing?"

# With vision detection (recommended)
python qwen_main.py --query "What are the latest advancements in quantum computing?" --debug

# With specific vision model
python qwen_main.py --query "What are the latest advancements in quantum computing?" --model "Qwen/Qwen2.5-VL-7B"

# Without vision detection (fallback)
python qwen_main.py --query "What are the latest advancements in quantum computing?" --no-vision
```

### Command-Line Arguments

- `--site`: Target site (default: "qwen")
- `--query`: Single query to send
- `--query-file`: File with multiple queries (one per line)
- `--browser`: Browser to use (default: "chrome")
- `--output-dir`: Directory to save responses (default: "responses")
- `--output-format`: Output format (txt, json, md) (default: "json")
- `--delay-min`: Minimum delay between queries (default: 10 seconds)
- `--delay-max`: Maximum delay between queries (default: 30 seconds)
- `--wait-for-login`: Wait for user to manually log in
- `--debug`: Enable debug mode with screenshots
- `--no-vision`: Disable vision-based UI detection
- `--model`: Vision model to use (default: "Qwen/Qwen2.5-VL-7B")

## Vision Detection System

The system uses the Qwen-VL model to:

1. Dynamically locate UI elements like:
   - Chat input field
   - Send button
   - Response area

2. Extract responses using vision rather than relying on hard-coded positions

3. Detect CAPTCHAs and verification challenges

## Supported Models

- `Qwen/Qwen2.5-VL-7B` - Default option, good balance of performance and accuracy
- `Qwen/Qwen2.5-VL-4B` - Smaller model, faster but less accurate
- `Qwen/Qwen-VL-Chat` - Older model, may not work as well with newer interfaces
- `Qwen/Qwen2-VL` - Alternative model if the default isn't available

## Troubleshooting

### Vision Detection Issues

If the system fails to detect UI elements:

1. Run with `--debug` to save screenshots of detection attempts
2. Try a different model using `--model` parameter
3. If vision detection continues to fail, use `--no-vision` to fall back to traditional automation

### General Issues

- **Login Problems**: Use `--wait-for-login` to manually log in
- **CAPTCHA Detection**: The system will pause and notify you if it detects a CAPTCHA
- **Browser Issues**: Try closing all browser windows and letting the script start a fresh instance

## Implementation Details

The implementation consists of several key components:

- `qwen_main.py`: Main entry point for the CLI
- `src/qwen_processor.py`: Handles vision model loading and UI detection
- `src/ui_automation.py`: Provides automation for browser interaction
- `src/site_vision.py`: Contains site-specific implementations for chat.qwen.ai
- `src/vision_detection.py`: Core vision detection logic using Qwen-VL

## Example Output

When running with debug mode enabled, the system will save screenshots to a debug directory, showing:

- UI element detection
- CAPTCHA detection (if any)
- Response extraction

The extracted responses are saved in the specified output directory in the requested format (JSON, TXT, or MD).

## Advanced Usage

### Custom Prompting

For specific tasks, you can create a queries file:

```
# queries.txt
Explain the concept of quantum entanglement
What is Qwen AI and how does it work?
Compare Qwen AI with other large language models
```

Then run:

```bash
python qwen_main.py --query-file queries.txt --output-format md
```

### Continuous Operation

For continuous operation with multiple queries:

```bash
python qwen_main.py --query-file queries.txt --delay-min 30 --delay-max 120
```

This will space out queries by 30-120 seconds to appear more human-like.

## License

This project is licensed under the MIT License - see the LICENSE file for details.