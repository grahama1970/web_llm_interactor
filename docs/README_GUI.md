# GUI Automation for AI Chat Interactions

This approach uses OS-level GUI automation rather than browser automation to interact with AI chat sites, making it much harder for sites to detect it as a bot.

## Why This Approach Works Better

1. **Bypasses Browser Fingerprinting**: Since you're controlling a real browser installed on your system (not a headless or automated one), you avoid most browser fingerprinting detection.

2. **Natural Interactions**: The script simulates human-like mouse movements, typing patterns, and timing, making it appear more natural.

3. **No WebDriver Signatures**: There are no WebDriver or automation signatures for sites to detect.

4. **Uses Real Browser Profiles**: Your regular browser with all cookies, extensions, and history is used, making it look like a legitimate user.

## Requirements

```bash
pip install -r requirements_gui.txt
```

You'll also need to install Tesseract OCR:

- macOS: `brew install tesseract`
- Ubuntu: `sudo apt-get install tesseract-ocr`
- Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki

## Usage

Basic usage:

```bash
python gui_automation.py --site qwen
```

Options:
- `--site`: Choose between "qwen" or "perplexity"
- `--question`: Specify a custom question (otherwise a default is used)

## Setup Instructions

### 1. Creating Reference Images

Before running the script, you need to create reference screenshots of UI elements:

1. Open the target website manually
2. Take screenshots of:
   - The input field/textarea
   - Any buttons you need to click
   - Save them as PNG files (e.g., `qwen_input.png`, `perplexity_input.png`)

### 2. Adjusting for Your Screen Resolution

The script uses image recognition to find elements on screen, which is resolution-dependent. Make sure to:

1. Take screenshots at the same resolution you'll run the script
2. Adjust confidence levels if needed (`find_and_click_image` function)

### 3. CAPTCHA Handling

When a CAPTCHA is detected, the script will pause and ask you to solve it manually, then continue once you press Enter.

## How It Works

1. The script opens your default browser with the target URL
2. It waits for the page to load and checks for CAPTCHAs
3. It finds the input field using image recognition
4. It types the question with human-like timing and presses Enter
5. It waits for and captures the response

## Limitations

- Requires a graphical environment (won't work on headless servers)
- Screen resolution dependent
- May require manual CAPTCHA solving the first time
- The browser window must remain visible and active during operation

## Advanced Usage

You can modify the script to:
- Handle more complex interactions
- Save responses in structured formats
- Run on a schedule using a tool like cron
- Add more sophisticated image recognition

## Troubleshooting

- If elements aren't being found, try adjusting the confidence level in the `find_and_click_image` function
- Make sure the browser window is fully visible and not obscured
- Check the log file for detailed information about what's happening