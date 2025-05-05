#!/bin/bash
# Simple shell script wrapper for the AppleScript

# Check if text argument is provided
if [ -z "$1" ]; then
  echo "Error: Please provide text to paste."
  echo "Usage: ./paste_to_chat.sh \"Your text here\""
  exit 1
fi

# Print instructions
echo "============================================================"
echo "AppleScript Chat Paste Utility"
echo "============================================================"
echo "Text to send: $1"
echo "============================================================"
echo ""
echo "Instructions:"
echo "1. Switch to your browser window"
echo "2. Click on the chat input field"
echo "3. Return to terminal and press Enter when ready..."

# Wait for user to be ready
read -p ""

# Execute the AppleScript
echo "Pasting text..."
osascript paste_to_chat.scpt "$1"

echo ""
echo "Done!"