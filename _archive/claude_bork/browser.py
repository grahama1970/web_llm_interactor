#!/usr/bin/env python3
"""
Browser management module for AI Chat Automation
"""

import os
import sys
import time
import subprocess
import logging
import pyautogui
import psutil
from enum import Enum
from typing import List, Dict, Tuple, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("browser.log"),
        logging.StreamHandler()
    ]
)

class BrowserType(Enum):
    """Supported browser types"""
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"

class Browser:
    """Manages browser interaction at the OS level"""
    
    def __init__(self, browser_type: Union[BrowserType, str] = BrowserType.CHROME):
        """
        Initialize browser manager
        
        Args:
            browser_type: Type of browser to target (chrome, firefox, safari, edge)
        """
        if isinstance(browser_type, str):
            try:
                self.browser_type = BrowserType(browser_type.lower())
            except ValueError:
                logging.warning(f"Unsupported browser type: {browser_type}. Defaulting to Chrome.")
                self.browser_type = BrowserType.CHROME
        else:
            self.browser_type = browser_type
            
        # Process information
        self.process = None
        self.pid = None
        self.window_title = None
        self.window_handle = None
        
        # Platform-specific configurations
        self.is_macos = sys.platform == 'darwin'
        self.is_windows = sys.platform == 'win32'
        self.is_linux = not (self.is_macos or self.is_windows)
        
        # Browser executable and process names by platform
        self.browser_process_names = self._get_browser_process_names()
        
        logging.info(f"Initialized browser manager for {self.browser_type.value}")
    
    def _get_browser_process_names(self) -> Dict[BrowserType, List[str]]:
        """Get browser process names for the current platform"""
        process_names = {
            BrowserType.CHROME: [],
            BrowserType.FIREFOX: [],
            BrowserType.SAFARI: [],
            BrowserType.EDGE: []
        }
        
        if self.is_macos:
            process_names[BrowserType.CHROME] = ["Google Chrome", "chrome"]
            process_names[BrowserType.FIREFOX] = ["firefox", "Firefox"]
            process_names[BrowserType.SAFARI] = ["Safari"]
            process_names[BrowserType.EDGE] = ["Microsoft Edge", "msedge"]
        elif self.is_windows:
            process_names[BrowserType.CHROME] = ["chrome.exe"]
            process_names[BrowserType.FIREFOX] = ["firefox.exe"]
            process_names[BrowserType.EDGE] = ["msedge.exe"]
        else:  # Linux
            process_names[BrowserType.CHROME] = ["chrome", "chromium"]
            process_names[BrowserType.FIREFOX] = ["firefox"]
            process_names[BrowserType.EDGE] = ["msedge"]
        
        return process_names
    
    def find_process(self) -> bool:
        """Find a running browser process"""
        for proc in psutil.process_iter(['pid', 'name']):
            process_name = proc.info['name']
            if any(browser_name.lower() in process_name.lower() 
                  for browser_name in self.browser_process_names[self.browser_type]):
                self.process = proc
                self.pid = proc.info['pid']
                logging.info(f"Found {self.browser_type.value} process with PID {self.pid}")
                return True
        
        logging.warning(f"No running {self.browser_type.value} process found")
        return False
    
    def launch_if_needed(self, url: Optional[str] = None) -> bool:
        """Launch browser if not already running"""
        if self.find_process():
            logging.info(f"Browser {self.browser_type.value} already running")
            return True
        
        logging.info(f"Launching browser {self.browser_type.value}")
        return self._launch_browser(url)
    
    def _launch_browser(self, url: Optional[str] = None) -> bool:
        """Launch browser with optional URL"""
        browser_cmd = self._get_browser_launch_command()
        if not browser_cmd:
            logging.error(f"Could not determine launch command for {self.browser_type.value}")
            return False
        
        # Add URL if provided
        if url:
            browser_cmd.append(url)
        
        try:
            subprocess.Popen(browser_cmd)
            time.sleep(3)  # Wait for browser to start
            return self.find_process()
        except Exception as e:
            logging.error(f"Error launching browser: {e}")
            return False
    
    def _get_browser_launch_command(self) -> List[str]:
        """Get platform-specific browser launch command"""
        if self.is_macos:
            if self.browser_type == BrowserType.CHROME:
                return ["open", "-a", "Google Chrome"]
            elif self.browser_type == BrowserType.FIREFOX:
                return ["open", "-a", "Firefox"]
            elif self.browser_type == BrowserType.SAFARI:
                return ["open", "-a", "Safari"]
            elif self.browser_type == BrowserType.EDGE:
                return ["open", "-a", "Microsoft Edge"]
        elif self.is_windows:
            if self.browser_type == BrowserType.CHROME:
                return ["start", "chrome"]
            elif self.browser_type == BrowserType.FIREFOX:
                return ["start", "firefox"]
            elif self.browser_type == BrowserType.EDGE:
                return ["start", "msedge"]
        else:  # Linux
            if self.browser_type == BrowserType.CHROME:
                # Try different possibilities
                for cmd in ["google-chrome", "chrome", "chromium-browser", "chromium"]:
                    if subprocess.run(["which", cmd], capture_output=True, text=True).returncode == 0:
                        return [cmd]
            elif self.browser_type == BrowserType.FIREFOX:
                return ["firefox"]
            elif self.browser_type == BrowserType.EDGE:
                return ["microsoft-edge"]
        
        return []
    
    def find_windows(self) -> List[str]:
        """Find browser windows using platform-specific methods"""
        if not self.pid and not self.find_process():
            return []
            
        if self.is_macos:
            return self._find_macos_windows()
        elif self.is_windows:
            return self._find_windows_windows()
        else:  # Linux
            return self._find_linux_windows()
    
    def _find_macos_windows(self) -> List[str]:
        """Find browser windows on macOS using AppleScript"""
        browser_name = {
            BrowserType.CHROME: "Google Chrome",
            BrowserType.FIREFOX: "Firefox",
            BrowserType.SAFARI: "Safari",
            BrowserType.EDGE: "Microsoft Edge"
        }.get(self.browser_type, "Google Chrome")
        
        script = f'''
        tell application "{browser_name}"
            set windowTitles to {{}}
            repeat with w in windows
                copy name of w to end of windowTitles
            end repeat
            return windowTitles
        end tell
        '''
        
        try:
            result = subprocess.check_output(['osascript', '-e', script], text=True)
            window_titles = [title.strip() for title in result.strip().split(',')]
            
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
    
    def _find_windows_windows(self) -> List[str]:
        """Find browser windows on Windows"""
        try:
            # This requires the pywin32 package
            import win32gui
            
            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    # Match browser window by title patterns
                    browser_patterns = {
                        BrowserType.CHROME: ["chrome", "google chrome"],
                        BrowserType.FIREFOX: ["firefox", "mozilla"],
                        BrowserType.EDGE: ["edge", "microsoft edge"],
                    }.get(self.browser_type, ["chrome"])
                    
                    if title and any(pattern in title.lower() for pattern in browser_patterns):
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
    
    def _find_linux_windows(self) -> List[str]:
        """Find browser windows on Linux using xdotool"""
        browser_class = {
            BrowserType.CHROME: "chrome",
            BrowserType.FIREFOX: "firefox",
            BrowserType.EDGE: "msedge"
        }.get(self.browser_type, "chrome")
        
        try:
            output = subprocess.check_output(
                ["xdotool", "search", "--class", browser_class, "getwindowname"], 
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
    
    def focus_window(self, window_title: Optional[str] = None) -> bool:
        """Focus on a specific browser window or the first one found"""
        if window_title:
            self.window_title = window_title
        
        if not self.window_title:
            windows = self.find_windows()
            if not windows:
                logging.error("No browser windows to focus")
                return False
        
        if self.is_macos:
            return self._focus_macos_window()
        elif self.is_windows:
            return self._focus_windows_window()
        else:  # Linux
            return self._focus_linux_window()
    
    def _focus_macos_window(self) -> bool:
        """Focus browser window on macOS using AppleScript"""
        browser_name = {
            BrowserType.CHROME: "Google Chrome",
            BrowserType.FIREFOX: "Firefox",
            BrowserType.SAFARI: "Safari",
            BrowserType.EDGE: "Microsoft Edge"
        }.get(self.browser_type, "Google Chrome")
        
        script = f'''
        tell application "{browser_name}"
            activate
            if "{self.window_title}" is not "" then
                set index of window "{self.window_title}" to 1
            end if
        end tell
        '''
        
        try:
            subprocess.run(['osascript', '-e', script], check=True)
            logging.info(f"Focused browser window: {self.window_title or 'default'}")
            time.sleep(0.5)  # Wait for window to focus
            return True
        except Exception as e:
            logging.error(f"Error focusing macOS browser window: {e}")
            return False
    
    def _focus_windows_window(self) -> bool:
        """Focus browser window on Windows"""
        try:
            import win32gui
            if hasattr(self, 'window_handle'):
                win32gui.SetForegroundWindow(self.window_handle)
                logging.info(f"Focused browser window: {self.window_title}")
                time.sleep(0.5)  # Wait for window to focus
                return True
            return False
        except Exception as e:
            logging.error(f"Error focusing Windows browser window: {e}")
            return False
    
    def _focus_linux_window(self) -> bool:
        """Focus browser window on Linux using xdotool"""
        browser_class = {
            BrowserType.CHROME: "chrome",
            BrowserType.FIREFOX: "firefox",
            BrowserType.EDGE: "msedge"
        }.get(self.browser_type, "chrome")
        
        try:
            if self.window_title:
                subprocess.run(["xdotool", "search", "--name", self.window_title, "windowactivate"], check=True)
            else:
                subprocess.run(["xdotool", "search", "--class", browser_class, "windowactivate"], check=True)
            
            logging.info(f"Focused browser window: {self.window_title or 'default'}")
            time.sleep(0.5)  # Wait for window to focus
            return True
        except Exception as e:
            logging.error(f"Error focusing Linux browser window: {e}")
            return False
    
    def new_tab(self, url: Optional[str] = None) -> bool:
        """Open a new tab in the focused browser window"""
        if not self.focus_window():
            logging.error("Cannot open new tab: Failed to focus browser window")
            return False
        
        # Send keyboard shortcut for new tab
        if self.is_macos:
            pyautogui.hotkey('command', 't')
        else:  # Windows/Linux
            pyautogui.hotkey('ctrl', 't')
        
        time.sleep(1)
        
        # Navigate to URL if provided
        if url:
            self.navigate_to_url(url)
        
        logging.info(f"Opened new tab {f'with URL: {url}' if url else ''}")
        return True
    
    def navigate_to_url(self, url: str) -> bool:
        """Navigate to a URL in the current tab"""
        if not self.focus_window():
            logging.error("Cannot navigate: Failed to focus browser window")
            return False
        
        # Select the address bar
        if self.is_macos:
            pyautogui.hotkey('command', 'l')
        else:  # Windows/Linux
            pyautogui.hotkey('ctrl', 'l')
        
        time.sleep(0.5)
        
        # Clear current URL and enter new one
        pyautogui.hotkey('command' if self.is_macos else 'ctrl', 'a')
        time.sleep(0.2)
        pyautogui.write(url)
        time.sleep(0.2)
        pyautogui.press('enter')
        
        logging.info(f"Navigated to URL: {url}")
        time.sleep(2)  # Wait for page to start loading
        return True

# Example usage
if __name__ == "__main__":
    # Set up browser automation
    browser = Browser(BrowserType.CHROME)
    
    # Find existing browser or launch new one
    if not browser.find_process():
        browser.launch_if_needed()
    
    # Find and focus window
    browser.find_windows()
    browser.focus_window()
    
    # Open new tab and navigate to site
    browser.new_tab("https://chat.qwen.ai/")