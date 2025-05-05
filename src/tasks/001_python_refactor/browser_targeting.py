#!/usr/bin/env python3
"""
Browser targeting module for GUI automation
This module provides functions to detect, focus, and interact with 
already running browser instances instead of launching new ones.
"""

import os
import sys
import time
import subprocess
import logging
import pyautogui
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BrowserTarget:
    """Class to manage targeting and interacting with existing browser windows"""
    
    def __init__(self, browser_type="chrome"):
        """
        Initialize browser targeting
        
        Args:
            browser_type (str): Type of browser to target ("chrome", "safari", "firefox")
        """
        self.browser_type = browser_type.lower()
        self.process = None
        self.window_title = None
        self.browser_pid = None
        
        # Define browser-specific properties
        self.browser_process_names = {
            "chrome": ["Google Chrome", "chrome", "chrome.exe"],
            "safari": ["Safari", "safari"],
            "firefox": ["Firefox", "firefox", "firefox.exe"]
        }
    
    def find_browser_process(self):
        """Find running browser process by name"""
        for proc in psutil.process_iter(['pid', 'name']):
            process_name = proc.info['name']
            if any(browser_name in process_name for browser_name in self.browser_process_names.get(self.browser_type, [])):
                self.process = proc
                self.browser_pid = proc.info['pid']
                logging.info(f"Found {self.browser_type} process with PID {self.browser_pid}")
                return True
        
        logging.warning(f"No running {self.browser_type} process found")
        return False
    
    def find_browser_windows(self):
        """Find browser windows using platform-specific methods"""
        if not self.browser_pid:
            self.find_browser_process()
            if not self.browser_pid:
                return False
        
        if sys.platform == 'darwin':  # macOS
            return self._find_macos_browser_windows()
        elif sys.platform == 'win32':  # Windows
            return self._find_windows_browser_windows()
        else:  # Linux
            return self._find_linux_browser_windows()
    
    def _find_macos_browser_windows(self):
        """Find browser windows on macOS using AppleScript"""
        script = f'''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            set allProcesses to application processes
            set browserWindows to {}
            
            repeat with proc in allProcesses
                if name of proc contains "{self.browser_type}" then
                    set browserWindows to windows of proc
                    exit repeat
                end if
            end repeat
            
            set windowTitles to {}
            repeat with win in browserWindows
                copy name of win to end of windowTitles
            end repeat
            
            return windowTitles
        end tell
        '''
        
        try:
            result = subprocess.check_output(['osascript', '-e', script], text=True)
            window_titles = result.strip().split(', ')
            
            if window_titles:
                self.window_title = window_titles[0]  # Use the first window by default
                logging.info(f"Found browser windows: {window_titles}")
                return window_titles
            else:
                logging.warning("No browser windows found")
                return []
        except Exception as e:
            logging.error(f"Error finding macOS browser windows: {e}")
            return []
    
    def _find_windows_browser_windows(self):
        """Find browser windows on Windows"""
        try:
            # This requires the pywin32 package
            import win32gui
            
            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title and self.browser_type in title.lower():
                        windows.append((hwnd, title))
            
            windows = []
            win32gui.EnumWindows(callback, windows)
            
            if windows:
                self.window_handle = windows[0][0]
                self.window_title = windows[0][1]
                logging.info(f"Found browser windows: {[w[1] for w in windows]}")
                return [w[1] for w in windows]
            else:
                logging.warning("No browser windows found")
                return []
        except Exception as e:
            logging.error(f"Error finding Windows browser windows: {e}")
            return []
    
    def _find_linux_browser_windows(self):
        """Find browser windows on Linux using xdotool"""
        try:
            output = subprocess.check_output(
                ["xdotool", "search", "--class", self.browser_type, "getwindowname"], 
                text=True
            )
            window_titles = output.strip().split('\n')
            
            if window_titles:
                self.window_title = window_titles[0]
                logging.info(f"Found browser windows: {window_titles}")
                return window_titles
            else:
                logging.warning("No browser windows found")
                return []
        except Exception as e:
            logging.error(f"Error finding Linux browser windows: {e}")
            return []
    
    def focus_browser_window(self, window_title=None):
        """Focus on a specific browser window or the first one found"""
        if window_title:
            self.window_title = window_title
        
        if not self.window_title:
            windows = self.find_browser_windows()
            if not windows:
                logging.error("No browser windows to focus")
                return False
        
        if sys.platform == 'darwin':  # macOS
            return self._focus_macos_browser_window()
        elif sys.platform == 'win32':  # Windows
            return self._focus_windows_browser_window()
        else:  # Linux
            return self._focus_linux_browser_window()
    
    def _focus_macos_browser_window(self):
        """Focus browser window on macOS using AppleScript"""
        browser_app = "Google Chrome" if self.browser_type == "chrome" else self.browser_type.capitalize()
        
        script = f'''
        tell application "{browser_app}"
            activate
            if "{self.window_title}" is not "" then
                set index of window "{self.window_title}" to 1
            end if
        end tell
        '''
        
        try:
            subprocess.run(['osascript', '-e', script], check=True)
            logging.info(f"Focused browser window: {self.window_title or 'default'}")
            time.sleep(0.5)  # Give time for window to focus
            return True
        except Exception as e:
            logging.error(f"Error focusing macOS browser window: {e}")
            return False
    
    def _focus_windows_browser_window(self):
        """Focus browser window on Windows"""
        try:
            import win32gui
            if hasattr(self, 'window_handle'):
                win32gui.SetForegroundWindow(self.window_handle)
                logging.info(f"Focused browser window: {self.window_title}")
                time.sleep(0.5)  # Give time for window to focus
                return True
            return False
        except Exception as e:
            logging.error(f"Error focusing Windows browser window: {e}")
            return False
    
    def _focus_linux_browser_window(self):
        """Focus browser window on Linux using xdotool"""
        try:
            if self.window_title:
                subprocess.run(["xdotool", "search", "--name", self.window_title, "windowactivate"], check=True)
            else:
                subprocess.run(["xdotool", "search", "--class", self.browser_type, "windowactivate"], check=True)
            
            logging.info(f"Focused browser window: {self.window_title or 'default'}")
            time.sleep(0.5)  # Give time for window to focus
            return True
        except Exception as e:
            logging.error(f"Error focusing Linux browser window: {e}")
            return False
    
    def open_new_tab(self, url=None):
        """Open a new tab in the browser"""
        if not self.focus_browser_window():
            return False
        
        # Send keyboard shortcut for new tab
        if sys.platform == 'darwin':  # macOS
            pyautogui.hotkey('command', 't')
        else:  # Windows/Linux
            pyautogui.hotkey('ctrl', 't')
        
        time.sleep(1)
        
        # Navigate to URL if provided
        if url:
            pyautogui.write(url)
            pyautogui.press('enter')
            time.sleep(2)  # Wait for page to start loading
        
        logging.info(f"Opened new tab {f'with URL: {url}' if url else ''}")
        return True
    
    def navigate_to_url(self, url):
        """Navigate to a URL in the current tab"""
        if not self.focus_browser_window():
            return False
        
        # Select the address bar
        if sys.platform == 'darwin':  # macOS
            pyautogui.hotkey('command', 'l')
        else:  # Windows/Linux
            pyautogui.hotkey('ctrl', 'l')
        
        time.sleep(0.5)
        
        # Clear current URL and enter new one
        pyautogui.hotkey('command' if sys.platform == 'darwin' else 'ctrl', 'a')
        pyautogui.write(url)
        pyautogui.press('enter')
        
        logging.info(f"Navigated to URL: {url}")
        time.sleep(2)  # Wait for page to start loading
        return True

# Example usage
if __name__ == "__main__":
    browser = BrowserTarget("chrome")
    if browser.find_browser_process():
        windows = browser.find_browser_windows()
        print(f"Found {len(windows)} windows: {windows}")
        
        if windows:
            browser.focus_browser_window()
            # browser.open_new_tab("https://chat.qwen.ai/")
            browser.navigate_to_url("https://chat.qwen.ai/")