# Text Paste Tool for AI Chat Interfaces

This utility allows you to paste text into chat interfaces (like Perplexity, Qwen, etc.) using vision-based element detection. It uses computer vision to find the input field and send button on screen, then automatically pastes your text and sends it.

## Features

- Uses vision models to detect the chat input field and send button
- Works with different chat interfaces (auto-detection or specify the site)
- Compresses screenshots before processing to improve performance
- Human-like mouse movement and typing simulation
- Debug mode that saves screenshots of the process

## Installation

1. Make sure you have Python 3.7+ installed
2. Install dependencies:

```bash
pip install pyautogui numpy pyperclip pytesseract torch transformers pillow
```

## Usage

Basic usage:
```bash
python paste_text.py "Your message to send"
```

With more options:
```bash
python paste_text.py "Your message to send" --site perplexity --debug --wait 5
```

Or read text from a file:
```bash
python paste_text.py --file message.txt
```

You can also pipe content:
```bash
echo "This is a test" | python paste_text.py
```

### Command-line Options

- `text`: Text to paste (positional argument, optional)
- `-f, --file FILE`: Read text from a file
- `-s, --site {auto,qwen,perplexity}`: Target site identifier (default: auto)
- `-d, --debug`: Enable debug mode with screenshots
- `-w, --wait WAIT`: Time to wait before starting (to position window)
- `--no-keyboard`: Don't use keyboard shortcuts for pasting

## How It Works

1. The script captures a screenshot of your screen
2. A vision language model analyzes the screenshot to find the chat interface elements
3. Human-like mouse movements click on the input field
4. Text is pasted using clipboard or typed character by character
5. The send button is clicked to submit the message

## Vision Models

The script can use different vision models depending on what's available:

- `microsoft/git-base-coco` (default): Good for element detection
- `Salesforce/blip-image-captioning-base`: Alternative option

## Tips for Use

1. Make sure your browser window with the chat interface is visible and active
2. Position the window so the input field and send button are clearly visible
3. Use the `--wait` parameter to give yourself time to set up the window
4. If detection fails, try with the `--debug` flag to see the screenshots

## Customization

You can customize the behavior by editing the source files:

- `src/text_paste_utils.py`: The main paste functionality
- `src/vision_detection.py`: Vision model and element detection
- `src/human_input.py`: Human-like input simulation

## Troubleshooting

- **Can't detect elements**: Make sure the chat interface is clearly visible
- **Text doesn't paste**: Try using `--no-keyboard` flag to avoid keyboard shortcuts
- **Wrong elements detected**: Specify the site with `--site` parameter
- **Model loading errors**: Check your torch/transformers installation