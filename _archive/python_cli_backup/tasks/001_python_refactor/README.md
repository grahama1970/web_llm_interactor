# Enhanced GUI Automation for AI Chat Services

This refactored implementation provides sophisticated OS-level GUI automation to interact with AI chat services like Qwen, Perplexity, ChatGPT, and others, using advanced human-like interaction patterns to bypass bot detection.

## Key Features

### 1. Browser Targeting
The `browser_targeting.py` module allows the automation to work with already running browser instances:

- Detects existing Chrome/Firefox/Safari windows
- Focuses and interacts with specific browser tabs
- Works across Windows, macOS, and Linux platforms
- Maintains your existing logged-in sessions

### 2. Advanced Human Simulation
The `human_simulation.py` module implements highly sophisticated human-like behavior:

- Multi-point Bézier curve mouse movements with natural acceleration/deceleration
- Realistic typing with variable speed, occasional errors and corrections
- Natural pauses and idle behaviors
- Reading simulation based on content length
- Randomized scrolling patterns

### 3. Task-Based Architecture
The entire system is organized as a series of logical tasks with checkmarks for progress tracking.

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Additional system requirements:
   - For Mac: `brew install tesseract`
   - For Linux: `sudo apt-get install tesseract-ocr xdotool`
   - For Windows: Install Tesseract OCR from GitHub

## Usage

### Basic Usage
```python
from browser_targeting import BrowserTarget
from human_simulation import HumanSimulation

# Target existing Chrome browser
browser = BrowserTarget("chrome")
browser.find_browser_process()
browser.focus_browser_window()

# Navigate to AI service
browser.navigate_to_url("https://chat.qwen.ai/")

# Create human simulation
human = HumanSimulation()

# Perform human-like interactions
human.move_mouse(500, 400)  # Move to input field position
human.click()
human.type_text("What are the latest advancements in quantum computing?")
```

### Advanced Options

The system provides extensive configuration options:

```python
# Configure human simulation parameters
human = HumanSimulation()
human.typing_speed_wpm = 65  # Words per minute
human.typing_irregularity = 0.3  # Timing variability
human.typo_probability = 0.02  # Chance of typos

# Customize mouse behavior
human.mouse_speed = 0.6
human.jitter_factor = 0.1
```

## Implementation Notes

### Browser Targeting
- Uses AppleScript on macOS, Win32 API on Windows, and xdotool on Linux
- Preserves all cookies, login sessions, and browser fingerprints
- Handles focus management across multiple windows and tabs

### Human Simulation
- Implements mathematically accurate Bézier curves with dynamic control points
- Models realistic typing patterns based on keyboard layout
- Simulates natural reading behavior with appropriate pauses and scrolling
- Adds occasional idle behaviors to mimic genuine human interaction

## Advantages Over Browser Automation

This approach completely bypasses most bot detection because:

1. It controls your regular browser, not a WebDriver instance
2. It preserves your normal cookies and login sessions
3. It generates genuinely human-like mouse and keyboard patterns
4. It operates at the OS level, not through JavaScript APIs that can be detected

## Required Components

### Reference Images
You'll need to create screenshots of specific UI elements for each site:
- Input field/text area
- Submit button
- Any other clickable elements

### Site-Specific Coordinates
For reliable operation, you should identify:
- Approximate coordinates of key UI elements
- Scroll positions for longer pages
- Areas to check for CAPTCHAs or error messages

## Future Enhancements
- Implement ML-based CAPTCHA detection
- Add automated screenshot analysis
- Create site-specific modules for common AI services
- Add multi-session management for batch processing