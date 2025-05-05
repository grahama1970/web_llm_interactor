# Vision-Enhanced AI Chat Automation

This enhanced version of the AI Chat Automation tool uses Qwen 2.5 VL (Vision-Language) model to dynamically detect UI elements, eliminating the need for hardcoded coordinates or template matching with static screenshots.

## Key Features

- **Dynamic UI Element Detection**: Uses Qwen 2.5 VL to find input fields, buttons, and response areas
- **CAPTCHA Detection**: Automatically detects CAPTCHAs using vision AI
- **Adaptive Response Extraction**: Reads and extracts AI responses directly from the screen
- **All Original Features**: Maintains human-like interaction patterns and OS-level control

## How It Works

1. **UI Detection**: The Qwen 2.5 VL model analyzes screen captures to locate:
   - Chat input fields
   - Send buttons
   - Response areas

2. **Intelligent Interaction**: Once elements are detected, the system:
   - Moves the cursor to the appropriate positions
   - Types with human-like patterns
   - Clicks buttons or presses Enter as needed

3. **Response Extraction**: After the AI responds, the system:
   - Uses vision model to read and extract the response text
   - Falls back to clipboard-based methods if needed

## Requirements

In addition to the base requirements, you'll need:

```bash
# Install PyTorch and Transformers
pip install torch torchvision transformers
```

For optimum performance, a GPU with CUDA support is recommended but not required.

## Usage

```bash
python vision_main.py --site qwen --query "What are the latest advancements in quantum computing?"
```

Advanced options:

```bash
python vision_main.py --site perplexity --query-file queries.txt --model "Qwen/Qwen2.5-VL-7B" --debug
```

### Command-Line Options

All options from the original CLI, plus:

- `--no-vision`: Disable vision-based detection (falls back to traditional methods)
- `--model`: Specify which vision-language model to use

## Advantages

1. **Resilient to UI Changes**: Adapts to interface updates without requiring new screenshots
2. **Works Across Resolutions**: Functions correctly regardless of screen size or scaling
3. **Theme Independent**: Works with light or dark themes and various UI customizations
4. **More Natural Interactions**: Targets UI elements more precisely

## Implementation Details

The system is built on these key components:

- **VisionDetector**: Handles image capture, model queries, and element detection
- **VisionAIChatSite**: Base class enhanced with vision capabilities
- **Site-specific handlers**: Specialized versions for different AI chat platforms

## Memory Considerations

The Qwen 2.5 VL model requires approximately:
- 7B parameter version: ~14GB VRAM or RAM
- 1.5B parameter version: ~3GB VRAM or RAM (lower quality but faster)

The model is loaded once at startup and shared across all operations to minimize memory impact.

## Troubleshooting

Vision recognition issues:
- Run with `--debug` to save screenshots of detection attempts
- Try alternative models with `--model` parameter
- If vision detection fails, use `--no-vision` to fall back to traditional methods

## Adding Support for New Sites

1. Subclass `VisionAIChatSite` in `site_vision.py`
2. Implement site-specific methods
3. Update the factory function to include your new site

## License

This project is licensed under the MIT License - see the LICENSE file for details.