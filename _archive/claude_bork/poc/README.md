# Vision-Based AI Chat Automation - Proof of Concept Scripts

This directory contains separate proof-of-concept scripts that demonstrate the core capabilities for vision-based automation of AI chat interfaces. These scripts use Qwen-VL vision models to detect and interact with UI elements without using traditional browser automation APIs, making them less detectable by bot-prevention measures.

## Why This Approach?

Traditional browser automation frameworks (like Selenium, Playwright) are easily detected by modern AI chat services like Qwen.ai and Perplexity.ai. This project takes a fundamentally different approach:

1. Uses vision-based detection with Qwen-VL to identify UI elements in screenshots
2. Uses PyAutoGUI to simulate human mouse and keyboard interactions at the OS level
3. Operates completely outside of browser automation mechanisms
4. Creates a workflow that's nearly indistinguishable from human interaction

## Requirements

- Python 3.8+
- PyTorch (see notes for Intel Mac users)
- PyAutoGUI
- Transformers
- Qwen-VL models from Hugging Face

## Script Overview

### 1. `detect_chat_input.py`

Tests the core capability of detecting the chat input field using Qwen-VL vision model.

```
python detect_chat_input.py
```

This script:
- Takes a screenshot of your current screen
- Uses Qwen-VL to analyze and detect the chat input field
- Shows and saves the coordinates of the detected input area
- Visualizes the detection with a bounding box

### 2. `paste_to_chat.py`

Tests detecting the chat input field and pasting text into it.

```
# These two commands are equivalent:
python paste_to_chat.py "Your question here"
python paste_to_chat.py --query "Your question here"
```

This script:
- Takes a screenshot of your current screen
- Detects the chat input field
- Moves the mouse with human-like motion to the input field
- Clicks the input field
- Types or pastes the provided text
- Presses Enter to send the message

### 3. `captcha_detector.py`

Tests CAPTCHA detection capability to pause automation when human intervention is needed.

```
python captcha_detector.py [--wait 60] [--monitor]
```

This script:
- Takes a screenshot of your current screen
- Analyzes it to detect CAPTCHA challenges
- Can wait for manual CAPTCHA solution (with --wait option)
- Can continuously monitor for CAPTCHAs appearing (with --monitor option)

### 4. `extract_response.py`

Tests the capability to extract the AI's response text from the chat interface.

```
python extract_response.py [--site qwen|perplexity|generic] [--include-query]
```

This script:
- Takes a screenshot of your current screen
- Uses Qwen-VL to extract the AI response text
- Can also extract the user query (with --include-query option)
- Saves the extracted text in various formats

## Compatibility with Intel Macs

### ⚠️ IMPORTANT: Run the Intel Mac setup first ⚠️

If you're on an Intel Mac, run the main Intel Mac setup script from the project root directory before using these POC scripts:

```bash
cd ../../  # Go back to project root if you're in the poc directory
./install_intel_mac.sh
cd src/poc  # Return to the POC directory
```

This will install the nightly build of PyTorch with MPS support for Intel Macs and set the required environment variable `PYTORCH_ENABLE_MPS_FALLBACK=1`.

### Fallback Option

If the installation above doesn't work for any reason, you can use the included fallback script:

```bash
python fix_torch.py
```

This will install an older PyTorch version (1.13.1) that works on Intel Macs with macOS Monterey. While this version doesn't support MPS, it will work correctly on CPU.

All POC scripts have been updated to handle both configurations and will automatically fall back to CPU if MPS is not available.

## Customization

You can modify the prompts used for vision detection in each script to better match the specific UI elements of your target website. Look for the prompt variables in each script.

## Debug Output

All scripts save screenshots and debug information in the `debug` directory, which can help diagnose detection issues or improve the prompts.

## Common Parameters

Most scripts support these parameters:

- `--model`: Specify a different Qwen-VL model
- `--timeout`: Seconds to wait before capturing the screenshot
- `--debug`: Enable extra debug output

## Full Integration

These individual components are integrated into a complete system in the main `qwen_main.py` script in the parent directory, which combines all these capabilities into a seamless workflow.