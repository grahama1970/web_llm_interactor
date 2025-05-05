#!/usr/bin/osascript

-- Simple AppleScript to paste text to active window
-- Usage: osascript paste_to_chat.scpt "Your text here"

on run argv
  -- Get the text to paste from command-line argument
  set textToPaste to item 1 of argv
  
  -- Store current clipboard content
  set previousClipboard to the clipboard
  
  -- Copy text to clipboard
  set the clipboard to textToPaste
  
  -- Wait a moment
  delay 0.5
  
  -- Paste to active window
  tell application "System Events"
    keystroke "v" using {command down}
    delay 0.5
    keystroke return
  end tell
  
  -- Wait a moment
  delay 0.5
  
  -- Restore previous clipboard (optional)
  set the clipboard to previousClipboard
  
  return "Message sent: " & textToPaste
end run