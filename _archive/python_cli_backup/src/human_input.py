#!/usr/bin/env python3
"""
Human-like input simulation module
"""

import time
import random
import math
import logging
import sys
import pyautogui
import numpy as np
from typing import Tuple, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("human_input.log"),
        logging.StreamHandler()
    ]
)

class HumanInput:
    """Simulates human-like input for mouse and keyboard"""
    
    def __init__(self):
        """Initialize human input simulation with configurable parameters"""
        # Typing parameters
        self.typing_speed = random.uniform(40, 100)  # Words per minute
        self.typing_variability = random.uniform(0.2, 0.5)  # Timing variability
        self.typo_probability = 0.02  # Probability of making a typo
        self.correction_delay = (0.3, 1.0)  # Time before correcting typos
        
        # Mouse movement parameters
        self.movement_speed = random.uniform(0.3, 0.8)  # Base movement speed
        self.mouse_acceleration = random.uniform(0.5, 0.9)  # Accel/decel factor
        self.jitter_amount = random.uniform(0.05, 0.15)  # Movement jitter
        
        # Behavior parameters
        self.pause_frequency = 0.03  # Frequency of random pauses
        self.pause_duration = (0.3, 2.0)  # Range of pause durations
        self.reading_speed = random.uniform(150, 350)  # Words per minute for reading
        
        # Screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        logging.info(f"Screen dimensions: {self.screen_width}x{self.screen_height}")
    
    def _generate_bezier_points(
        self, 
        start: Tuple[int, int], 
        end: Tuple[int, int], 
        control_points_count: int = 2
    ) -> List[Tuple[float, float]]:
        """
        Generate control points for a Bézier curve between start and end points
        
        Args:
            start: Starting coordinates (x, y)
            end: Ending coordinates (x, y)
            control_points_count: Number of control points to generate
            
        Returns:
            List of all points including start, control points, and end
        """
        points = [start]
        
        # Calculate distance between start and end
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Normalize direction vector
        if distance > 0:
            nx = dx / distance
            ny = dy / distance
        else:
            # If start and end are the same, use a default direction
            nx, ny = 1, 0
        
        # Create perpendicular vector for control point displacement
        px, py = -ny, nx
        
        # Generate random control points
        for i in range(control_points_count):
            # Position along the path (not uniformly distributed)
            t = (i + 1) / (control_points_count + 1)
            
            # Add some randomness to t to make the control points less evenly spaced
            t = t * random.uniform(0.8, 1.2)
            t = max(0.1, min(0.9, t))  # Keep within reasonable bounds
            
            # Base point along the direct path
            bx = start[0] + t * dx
            by = start[1] + t * dy
            
            # Control point offset perpendicular to the path
            # Using a sinusoidal distribution for more natural curves
            offset_distance = distance * random.uniform(0.1, 0.4) * math.sin(math.pi * t)
            
            # Add some randomness to the offset direction
            offset_angle = random.uniform(-0.5, 0.5) * math.pi
            offset_x = math.cos(offset_angle) * px - math.sin(offset_angle) * py
            offset_y = math.sin(offset_angle) * px + math.cos(offset_angle) * py
            
            # Final control point position
            cx = bx + offset_distance * offset_x
            cy = by + offset_distance * offset_y
            
            points.append((cx, cy))
        
        points.append(end)
        return points
    
    def _calculate_bezier_point(
        self, 
        points: List[Tuple[float, float]], 
        t: float
    ) -> Tuple[float, float]:
        """
        Calculate a point along a Bézier curve using De Casteljau's algorithm
        
        Args:
            points: List of points defining the curve (start, control points, end)
            t: Parameter between 0 and 1 indicating position along the curve
            
        Returns:
            (x, y) coordinates of the point on the curve
        """
        if len(points) == 1:
            return points[0]
        
        new_points = []
        for i in range(len(points) - 1):
            x = (1 - t) * points[i][0] + t * points[i+1][0]
            y = (1 - t) * points[i][1] + t * points[i+1][1]
            new_points.append((x, y))
        
        return self._calculate_bezier_point(new_points, t)
    
    def move_mouse(
        self, 
        x: int, 
        y: int, 
        duration: Optional[float] = None, 
        humanize: bool = True
    ) -> None:
        """
        Move mouse cursor to the specified coordinates with human-like movement
        
        Args:
            x: Target x coordinate
            y: Target y coordinate
            duration: Optional movement duration override
            humanize: Whether to apply human-like movement patterns
        """
        # Get current mouse position
        current_x, current_y = pyautogui.position()
        
        # If already at target position or very close, no need for complex movement
        distance = math.sqrt((x - current_x)**2 + (y - current_y)**2)
        if distance < 5:
            pyautogui.moveTo(x, y, duration=0.1)
            return
        
        # Skip humanization if requested
        if not humanize:
            pyautogui.moveTo(x, y, duration=duration or 0.5)
            return
        
        # Auto-calculate duration based on distance if not specified
        if duration is None:
            # Fitts' Law inspired duration calculation
            base_duration = 0.3 + 0.15 * math.log2(1 + distance / 100)
            duration = base_duration * random.uniform(0.9, 1.1)
            duration = max(0.3, min(2.0, duration))
        
        # More control points for longer distances
        control_points_count = max(2, min(5, int(distance / 300) + 1))
        
        # Generate bezier curve points
        points = self._generate_bezier_points(
            (current_x, current_y), 
            (x, y), 
            control_points_count=control_points_count
        )
        
        # Calculate number of steps based on distance and duration
        steps = max(20, min(150, int(distance / 5)))
        
        # Move mouse along the bezier curve
        start_time = time.time()
        end_time = start_time + duration
        
        for i in range(1, steps + 1):
            # Calculate progress parameter with acceleration/deceleration
            elapsed = time.time() - start_time
            if elapsed >= duration:
                break
                
            # Normalized time parameter with easing
            t_linear = elapsed / duration
            
            # Apply easing function (ease-in-out)
            t = t_linear * t_linear * (3 - 2 * t_linear) if t_linear < 0.5 else 0.5 + (t_linear - 0.5) * (1 - (t_linear - 0.5)) * 2
            
            # Calculate point on curve
            px, py = self._calculate_bezier_point(points, t)
            
            # Add subtle jitter
            # More jitter in the middle of the path, less at start/end
            jitter_factor = self.jitter_amount * 4 * t * (1 - t)
            px += random.uniform(-jitter_factor, jitter_factor) * 5
            py += random.uniform(-jitter_factor, jitter_factor) * 5
            
            # Move to the point
            try:
                pyautogui.moveTo(px, py)
            except:
                # Fallback if movement fails
                pass
            
            # Calculate time to next step
            next_t = (i + 1) / steps
            next_time = start_time + (next_t * duration)
            sleep_time = max(0, next_time - time.time())
            
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # Ensure we end exactly at the target position
        pyautogui.moveTo(x, y)
        
        # Occasionally add a tiny movement after reaching the target
        if random.random() < 0.3:
            time.sleep(random.uniform(0.05, 0.15))
            tiny_offset = random.uniform(-3, 3)
            pyautogui.moveRel(tiny_offset, tiny_offset, duration=0.05)
            time.sleep(random.uniform(0.05, 0.1))
            pyautogui.moveTo(x, y, duration=0.05)
    
    def click(
        self, 
        x: Optional[int] = None, 
        y: Optional[int] = None, 
        button: str = 'left', 
        clicks: int = 1, 
        interval: float = 0.1
    ) -> None:
        """
        Perform a human-like click operation
        
        Args:
            x, y: Target coordinates (uses current position if None)
            button: Mouse button to click ('left', 'right', 'middle')
            clicks: Number of clicks
            interval: Time between multiple clicks
        """
        # Move to position if specified
        if x is not None and y is not None:
            self.move_mouse(x, y)
        
        # Slight pause before clicking
        time.sleep(random.uniform(0.05, 0.2))
        
        # Perform click(s)
        for i in range(clicks):
            pyautogui.click(button=button)
            if i < clicks - 1:
                # Variable interval for multiple clicks
                actual_interval = interval * random.uniform(0.8, 1.2)
                time.sleep(actual_interval)
        
        # Occasional tiny mouse movement after clicking
        if random.random() < 0.3:
            current_x, current_y = pyautogui.position()
            offset_x = random.uniform(-5, 5)
            offset_y = random.uniform(-5, 5)
            pyautogui.moveRel(offset_x, offset_y, duration=0.1)
            time.sleep(random.uniform(0.05, 0.15))
            pyautogui.moveTo(current_x, current_y, duration=0.1)
    
    def double_click(
        self, 
        x: Optional[int] = None, 
        y: Optional[int] = None
    ) -> None:
        """
        Perform a human-like double-click
        
        Args:
            x, y: Target coordinates (uses current position if None)
        """
        self.click(x, y, clicks=2, interval=random.uniform(0.08, 0.15))
    
    def right_click(
        self, 
        x: Optional[int] = None, 
        y: Optional[int] = None
    ) -> None:
        """
        Perform a human-like right-click
        
        Args:
            x, y: Target coordinates (uses current position if None)
        """
        self.click(x, y, button='right')
    
    def _get_keyboard_neighbors(self, char: str) -> str:
        """Get neighboring keys for a given character on QWERTY keyboard"""
        keyboard_layout = {
            'q': 'was', 'w': 'qase', 'e': 'wsdr', 'r': 'edft', 't': 'rfgy',
            'y': 'tghu', 'u': 'yhji', 'i': 'ujko', 'o': 'iklp', 'p': 'ol',
            'a': 'qwsz', 's': 'awedxz', 'd': 'serfcx', 'f': 'drtgvc', 'g': 'ftyhbv',
            'h': 'gyujnb', 'j': 'huikmn', 'k': 'jiolm', 'l': 'kop',
            'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn',
            'n': 'bhjm', 'm': 'njk', ' ': 'bnm,'
        }
        
        char_lower = char.lower()
        if char_lower in keyboard_layout:
            neighbors = keyboard_layout[char_lower]
            # Randomly select a neighbor
            typo_char = random.choice(neighbors)
            # Preserve case
            if char.isupper():
                return typo_char.upper()
            return typo_char
        return char
    
    def type_text(
        self, 
        text: str, 
        simulate_typos: bool = True, 
        typing_speed_override: Optional[float] = None
    ) -> None:
        """
        Type text with human-like patterns, including errors and corrections
        
        Args:
            text: Text to type
            simulate_typos: Whether to simulate occasional typos and corrections
            typing_speed_override: Optional override for typing speed (WPM)
        """
        if not text:
            return
        
        # Use override typing speed if provided
        typing_speed = typing_speed_override or self.typing_speed
        
        # Calculate base time per character from WPM
        # Average word length is ~5 characters
        chars_per_minute = typing_speed * 5
        base_delay = 60 / chars_per_minute
        
        # Type the text character by character
        i = 0
        while i < len(text):
            # Get current character
            char = text[i]
            
            # Decide if we're going to make a typo
            made_typo = False
            if simulate_typos and random.random() < self.typo_probability:
                made_typo = True
                
                # Choose typo type:
                # 1: wrong key, 2: double key, 3: missed key
                typo_type = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
                
                if typo_type == 1:  # Wrong key
                    # Type a neighboring key instead
                    wrong_char = self._get_keyboard_neighbors(char)
                    self._type_single_char(wrong_char, base_delay)
                    
                elif typo_type == 2:  # Double key
                    # Type the correct key twice
                    self._type_single_char(char, base_delay)
                    self._type_single_char(char, base_delay)
                    i += 1  # Move to next character
                    
                elif typo_type == 3:  # Missed key
                    # Skip this character, don't type anything
                    pass
                
                # "Notice" the error after a delay
                correction_delay = random.uniform(*self.correction_delay)
                time.sleep(correction_delay)
                
                # Error correction: backspace and fix
                if typo_type in (1, 2):
                    # For wrong key or double key, need backspace
                    pyautogui.press('backspace')
                    time.sleep(random.uniform(0.1, 0.3))
                
                # Now type the correct character
                if i < len(text):
                    self._type_single_char(text[i], base_delay)
            else:
                # Normal typing without error
                self._type_single_char(char, base_delay)
            
            # Proceed to next character
            i += 1
            
            # Add natural pauses
            # Longer pauses after sentence-ending punctuation
            if char in '.!?':
                time.sleep(random.uniform(0.5, 1.2))
            # Medium pauses after commas, semicolons, etc.
            elif char in ',:;-':
                time.sleep(random.uniform(0.3, 0.7))
            # Occasional random pauses during typing
            elif not made_typo and random.random() < self.pause_frequency:
                time.sleep(random.uniform(*self.pause_duration))
    
    def _type_single_char(self, char: str, base_delay: float) -> None:
        """Type a single character with natural timing variation"""
        # Add variability to timing
        delay = base_delay * random.uniform(
            1 - self.typing_variability,
            1 + self.typing_variability
        )
        
        # Special handling for shift key combinations
        if char.isupper() or char in '~!@#$%^&*()_+{}|:"<>?':
            # Hold shift, press the key, release shift
            with pyautogui.hold('shift'):
                if char.isupper():
                    pyautogui.press(char.lower())
                else:
                    # Map shifted special characters to their unshifted keys
                    shifted_map = {
                        '~': '`', '!': '1', '@': '2', '#': '3', '$': '4', '%': '5',
                        '^': '6', '&': '7', '*': '8', '(': '9', ')': '0', '_': '-',
                        '+': '=', '{': '[', '}': ']', '|': '\\', ':': ';',
                        '"': "'", '<': ',', '>': '.', '?': '/'
                    }
                    pyautogui.press(shifted_map.get(char, char))
        else:
            # Regular key press
            pyautogui.press(char)
        
        # Wait with variable delay
        time.sleep(delay)
    
    def scroll(
        self, 
        clicks: int, 
        duration: Optional[float] = None
    ) -> None:
        """
        Perform human-like scrolling
        
        Args:
            clicks: Number of scroll clicks (positive for down, negative for up)
            duration: Duration of the scrolling action
        """
        if clicks == 0:
            return
        
        # Determine scroll direction
        direction = 1 if clicks > 0 else -1
        clicks_abs = abs(clicks)
        
        # Auto-calculate duration if not specified
        if duration is None:
            duration = 0.3 + (clicks_abs / 10) * random.uniform(0.8, 1.2)
            duration = min(duration, 3.0)  # Cap at 3 seconds
        
        # Break scrolling into chunks
        remaining = clicks_abs
        chunk_size = min(5, max(1, clicks_abs // 10))
        
        start_time = time.time()
        end_time = start_time + duration
        
        while remaining > 0 and time.time() < end_time:
            # Calculate how much to scroll in this chunk
            current_chunk = min(remaining, chunk_size)
            
            # Add variability to chunk size
            current_chunk = max(1, int(current_chunk * random.uniform(0.8, 1.2)))
            
            # Determine timing for this chunk
            elapsed = time.time() - start_time
            progress = elapsed / duration if duration > 0 else 1.0
            
            # Scroll speed profile: accelerate, then decelerate
            if progress < 0.2:
                # Starting - accelerating
                scroll_factor = 0.3 + progress * 3.5
            elif progress > 0.8:
                # Ending - decelerating
                scroll_factor = 0.3 + (1 - progress) * 3.5
            else:
                # Middle - full speed
                scroll_factor = 1.0
            
            # Apply variability to scroll speed
            scroll_factor *= random.uniform(0.9, 1.1)
            
            # Perform scroll
            actual_scroll = int(current_chunk * direction * scroll_factor)
            pyautogui.scroll(actual_scroll)
            
            remaining -= current_chunk
            
            # Small delay between scroll actions
            time.sleep(random.uniform(0.01, 0.05))
            
            # Occasionally pause during scrolling
            if random.random() < 0.1:
                time.sleep(random.uniform(0.2, 0.5))
    
    def press_key(
        self, 
        key: str, 
        presses: int = 1, 
        interval: float = 0.1
    ) -> None:
        """
        Press a key with human-like timing
        
        Args:
            key: Key to press
            presses: Number of times to press the key
            interval: Time between presses
        """
        for i in range(presses):
            pyautogui.press(key)
            if i < presses - 1:
                time.sleep(interval * random.uniform(0.8, 1.2))
    
    def hotkey(self, *args: str) -> None:
        """
        Press a hotkey combination
        
        Args:
            *args: Keys to press in combination
        """
        pyautogui.hotkey(*args)
    
    def paste_text(self, text: str) -> None:
        """
        Paste text instead of typing it
        
        Args:
            text: Text to paste
        """
        # Copy text to clipboard
        import pyperclip
        pyperclip.copy(text)
        
        # Slight pause
        time.sleep(random.uniform(0.2, 0.5))
        
        # Paste using keyboard shortcut
        if sys.platform == 'darwin':  # macOS
            pyautogui.hotkey('command', 'v')
        else:  # Windows/Linux
            pyautogui.hotkey('ctrl', 'v')
    
    def random_idle(self, duration: float = 1.0) -> None:
        """
        Perform random idle behavior for a specified duration
        
        Args:
            duration: How long to perform idle behaviors
        """
        start_time = time.time()
        end_time = start_time + duration
        
        while time.time() < end_time:
            # Choose a random idle behavior
            behavior = random.choices(
                ['mouse_move', 'tiny_scroll', 'none'], 
                weights=[0.4, 0.3, 0.3]
            )[0]
            
            if behavior == 'mouse_move':
                # Small random mouse movement
                current_x, current_y = pyautogui.position()
                offset_x = random.randint(-50, 50)
                offset_y = random.randint(-50, 50)
                
                self.move_mouse(
                    current_x + offset_x,
                    current_y + offset_y,
                    duration=random.uniform(0.3, 0.7)
                )
                
                # Sometimes move back
                if random.random() < 0.7:
                    time.sleep(random.uniform(0.2, 0.5))
                    self.move_mouse(
                        current_x,
                        current_y,
                        duration=random.uniform(0.3, 0.5)
                    )
            
            elif behavior == 'tiny_scroll':
                # Small random scroll
                scroll_amount = random.randint(-3, 3)
                if scroll_amount != 0:
                    self.scroll(scroll_amount)
            
            # Wait before next idle behavior
            remaining = end_time - time.time()
            if remaining > 0:
                sleep_time = min(remaining, random.uniform(0.5, 2.0))
                time.sleep(sleep_time)

# Example usage
if __name__ == "__main__":
    # Create human input simulator
    human_input = HumanInput()
    
    # Wait for user to position window
    print("Please position your window, script will start in 3 seconds...")
    time.sleep(3)
    
    # Demo mouse movement
    current_x, current_y = pyautogui.position()
    target_x = current_x + 300
    target_y = current_y + 200
    human_input.move_mouse(target_x, target_y)
    
    # Demo clicking
    human_input.click()
    
    # Demo typing
    human_input.type_text("This is a demonstration of human-like typing with occasional typos and corrections.")
    
    # Demo scrolling
    human_input.scroll(10)
    time.sleep(1)
    human_input.scroll(-5)
    
    print("Demo completed!")