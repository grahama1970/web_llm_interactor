#!/usr/bin/env python3
"""
Human Simulation Module for GUI Automation
This module provides advanced functions to simulate human-like interactions
including natural cursor movement, typing patterns, and behavior patterns.
"""

import time
import random
import math
import pyautogui
import numpy as np
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class HumanSimulation:
    """Class for simulating human-like computer interactions"""
    
    def __init__(self):
        """Initialize human simulation with configurable parameters"""
        # Typing parameters
        self.typing_speed_wpm = random.uniform(40, 100)  # Words per minute
        self.typing_irregularity = random.uniform(0.2, 0.5)  # How much to vary timing
        self.typo_probability = 0.03  # Probability of making a typo
        self.correction_delay = (0.5, 1.5)  # Range of delay before correcting typos
        
        # Mouse movement parameters
        self.mouse_speed = random.uniform(0.3, 0.8)  # Base mouse movement speed
        self.mouse_acceleration = random.uniform(0.5, 0.9)  # Acceleration factor
        self.jitter_factor = random.uniform(0.05, 0.15)  # How much to jitter movement
        
        # Behavioral parameters
        self.attention_span = random.uniform(20, 60)  # Seconds before idle movement
        self.reading_speed_wpm = random.uniform(150, 350)  # Words per minute for reading
        self.decision_delay_range = (0.5, 3.0)  # Range of delays for decision points
        
        # Internal state
        self.last_action_time = time.time()
        self.current_activity = None
        
    def _calculate_bezier_curve(self, start_point, end_point, control_points_count=2, steps=100):
        """
        Calculate points along a Bézier curve with multiple control points
        
        Args:
            start_point: (x, y) starting coordinates
            end_point: (x, y) ending coordinates
            control_points_count: Number of control points to use
            steps: Number of points to calculate along the curve
            
        Returns:
            List of (x, y) points along the curve
        """
        # Generate random control points
        control_points = []
        for _ in range(control_points_count):
            # Create control point at random position between start and end
            # but with random variation perpendicular to the direct path
            t = random.uniform(0.2, 0.8)
            direct_x = start_point[0] + t * (end_point[0] - start_point[0])
            direct_y = start_point[1] + t * (end_point[1] - start_point[1])
            
            # Calculate perpendicular vector
            dx = end_point[0] - start_point[0]
            dy = end_point[1] - start_point[1]
            length = math.sqrt(dx*dx + dy*dy)
            
            if length < 1:  # Avoid division by zero
                length = 1
                
            # Perpendicular vector, scaled by distance and random factor
            perp_x = -dy / length * random.uniform(0.1, 0.5) * length
            perp_y = dx / length * random.uniform(0.1, 0.5) * length
            
            control_point = (direct_x + perp_x, direct_y + perp_y)
            control_points.append(control_point)
        
        # Create complete point list including start, control points, and end
        points = [start_point] + control_points + [end_point]
        n = len(points) - 1
        
        # Calculate points along the Bézier curve
        curve_points = []
        for i in range(steps + 1):
            t = i / steps
            
            # De Casteljau's algorithm for Bézier curve
            current_points = points.copy()
            for j in range(n):
                for k in range(n - j):
                    x = (1 - t) * current_points[k][0] + t * current_points[k + 1][0]
                    y = (1 - t) * current_points[k][1] + t * current_points[k + 1][1]
                    current_points[k] = (x, y)
            
            curve_points.append(current_points[0])
        
        return curve_points
    
    def _dynamic_mouse_speed(self, distance, point_idx, total_points):
        """
        Calculate dynamic mouse speed based on distance and position in path
        
        This simulates human acceleration/deceleration during movement
        """
        # Normalize position in curve (0 to 1)
        position = point_idx / total_points
        
        # Speed profile: start slow, accelerate, then decelerate at the end
        if position < 0.2:
            # Starting - accelerating
            speed_factor = 0.3 + position * 3.5
        elif position > 0.8:
            # Ending - decelerating
            speed_factor = 0.3 + (1 - position) * 3.5
        else:
            # Middle - full speed
            speed_factor = 1.0
        
        # Scale by distance - longer movements are faster
        distance_factor = min(1.0, distance / 500)
        
        # Apply base speed and variability
        final_speed = self.mouse_speed * speed_factor * (0.8 + distance_factor)
        
        # Add slight randomness
        final_speed *= random.uniform(0.9, 1.1)
        
        return final_speed
    
    def move_mouse(self, x, y, duration=None):
        """
        Move mouse to position with human-like movement
        
        Args:
            x, y: Target coordinates
            duration: Optional manual duration override
        """
        start_x, start_y = pyautogui.position()
        distance = math.sqrt((x - start_x)**2 + (y - start_y)**2)
        
        # Skip complex movement for tiny distances
        if distance < 5:
            pyautogui.moveTo(x, y, duration=0.1)
            return
        
        # Auto-calculate duration based on distance if not specified
        if duration is None:
            # Base duration on distance, with some randomness
            base_duration = distance / 1000
            duration = max(0.3, min(2.0, base_duration * random.uniform(0.8, 1.2)))
        
        # Generate more control points for longer distances
        control_points = max(2, min(5, int(distance / 200)))
        steps = max(50, min(200, int(distance / 10)))
        
        # Calculate curve
        curve_points = self._calculate_bezier_curve(
            (start_x, start_y), 
            (x, y), 
            control_points_count=control_points,
            steps=steps
        )
        
        # Move mouse along curve with dynamic timing
        previous_point = curve_points[0]
        total_points = len(curve_points)
        
        for i, point in enumerate(curve_points[1:], 1):
            point_x, point_y = point
            
            # Add subtle jitter to point position (more pronounced in the middle of the path)
            jitter_amount = self.jitter_factor * math.sin(math.pi * i/total_points)
            point_x += random.uniform(-jitter_amount, jitter_amount) * 5
            point_y += random.uniform(-jitter_amount, jitter_amount) * 5
            
            # Calculate movement speed for this segment
            segment_duration = self._dynamic_mouse_speed(distance, i, total_points)
            
            # Move to the point
            try:
                pyautogui.moveTo(point_x, point_y, duration=segment_duration)
            except:
                # Fallback if movement fails
                pyautogui.moveTo(point_x, point_y, duration=0.1)
            
            previous_point = point
        
        # Ensure we end at exactly the target position
        pyautogui.moveTo(x, y, duration=0.05)
        self.last_action_time = time.time()
    
    def click(self, x=None, y=None, button='left', clicks=1, interval=0.1):
        """
        Perform a human-like click operation
        
        Args:
            x, y: Optional coordinates (uses current position if None)
            button: Mouse button to click
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
                time.sleep(interval * random.uniform(0.8, 1.2))
        
        # Slight pause after clicking
        time.sleep(random.uniform(0.05, 0.2))
        self.last_action_time = time.time()
    
    def type_text(self, text, error_correction=True):
        """
        Type text with human-like patterns, including errors and corrections
        
        Args:
            text: Text to type
            error_correction: Whether to simulate typos and corrections
        """
        if not text:
            return
            
        # Calculate base time per character from WPM
        # Average word length is ~5 characters
        chars_per_minute = self.typing_speed_wpm * 5
        base_delay = 60 / chars_per_minute
        
        i = 0
        while i < len(text):
            char = text[i]
            
            # Simulate typo if enabled
            made_typo = False
            if error_correction and random.random() < self.typo_probability:
                made_typo = True
                
                # Choose a typo type (1: wrong key, 2: double key, 3: missed key)
                typo_type = random.randint(1, 3)
                
                if typo_type == 1:  # Wrong key
                    # Get a key near the intended key
                    keyboard_layout = {
                        'q': 'was', 'w': 'qase', 'e': 'wsdr', 'r': 'edft', 't': 'rfgy',
                        'y': 'tghu', 'u': 'yhji', 'i': 'ujko', 'o': 'iklp', 'p': 'ol',
                        'a': 'qwsz', 's': 'awedxz', 'd': 'serfcx', 'f': 'drtgvc', 'g': 'ftyhbv',
                        'h': 'gyujnb', 'j': 'huikmn', 'k': 'jiolm', 'l': 'kop',
                        'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn',
                        'n': 'bhjm', 'm': 'njk'
                    }
                    
                    # Get nearby keys or a random key if not found
                    if char.lower() in keyboard_layout:
                        nearby = keyboard_layout[char.lower()]
                        wrong_char = random.choice(nearby)
                        # Preserve case
                        if char.isupper():
                            wrong_char = wrong_char.upper()
                    else:
                        # Random typo for keys not in the layout
                        wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                    
                    # Type the wrong character
                    self._type_single_char(wrong_char)
                    
                elif typo_type == 2:  # Double key
                    # Type the correct key twice
                    self._type_single_char(char)
                    self._type_single_char(char)
                    i += 1  # Move to next character
                    
                elif typo_type == 3:  # Missed key
                    # Skip this character, don't type anything
                    pass
                
                # Pause to "notice" the error
                time.sleep(random.uniform(*self.correction_delay))
                
                # Error correction: backspace and fix
                if typo_type == 1 or typo_type == 2:
                    pyautogui.press('backspace')
                    time.sleep(random.uniform(0.1, 0.3))
                
                # If we missed a key, no need for backspace
                
                # Type the correct character
                if i < len(text):
                    self._type_single_char(text[i])
            else:
                # Normal typing without error
                self._type_single_char(char)
            
            # Proceed to next character
            i += 1
            
            # Pauses at punctuation
            if char in '.,:;?!':
                time.sleep(random.uniform(0.3, 0.8))
            
            # Occasionally pause while typing
            if not made_typo and random.random() < 0.03:
                time.sleep(random.uniform(0.5, 1.5))
                
        self.last_action_time = time.time()
    
    def _type_single_char(self, char):
        """Type a single character with natural timing variation"""
        # Calculate base time per character from WPM
        chars_per_minute = self.typing_speed_wpm * 5
        base_delay = 60 / chars_per_minute
        
        # Add irregularity to timing
        delay = base_delay * random.uniform(
            1 - self.typing_irregularity,
            1 + self.typing_irregularity
        )
        
        # Type the character
        pyautogui.write(char)
        
        # Wait with variable delay
        time.sleep(delay)
    
    def scroll_page(self, amount=None, direction='down', content_length=None):
        """
        Scroll page in a natural way, with variable speed and pauses
        
        Args:
            amount: Scroll amount (if None, calculated based on content_length)
            direction: 'up' or 'down'
            content_length: Optional content length in words to calculate reading time
        """
        # If no amount specified, use random amount
        if amount is None:
            amount = random.randint(3, 10) * 100
            
        # Adjust direction
        if direction == 'up':
            amount = -amount
            
        # Break scrolling into multiple smaller movements
        remaining = abs(amount)
        scroll_speed = random.uniform(10, 30)  # pixels per scroll
        
        while remaining > 0:
            # Calculate scroll chunk with variability
            chunk = min(remaining, scroll_speed * random.uniform(0.8, 1.2))
            
            # Determine scroll amount with proper sign
            scroll_amount = chunk if amount > 0 else -chunk
            
            # Perform scroll
            pyautogui.scroll(int(scroll_amount))
            
            # Pause between scrolls
            time.sleep(random.uniform(0.05, 0.2))
            
            remaining -= chunk
        
        # If content length is provided, pause for "reading"
        if content_length:
            reading_time = (content_length / self.reading_speed_wpm) * 60
            # Add variability to reading time
            reading_time *= random.uniform(0.7, 1.3)
            
            # Don't wait too long regardless of content length
            reading_time = min(reading_time, 10)
            
            # Log and wait
            logging.info(f"Reading content for {reading_time:.2f} seconds")
            time.sleep(reading_time)
        
        self.last_action_time = time.time()
    
    def random_idle_behavior(self):
        """Perform random idle behavior like small mouse movements or scrolls"""
        behavior = random.choice(['mouse_movement', 'small_scroll', 'none'])
        
        if behavior == 'mouse_movement':
            # Small random mouse movement
            current_x, current_y = pyautogui.position()
            offset_x = random.randint(-100, 100)
            offset_y = random.randint(-100, 100)
            self.move_mouse(current_x + offset_x, current_y + offset_y)
            time.sleep(random.uniform(0.5, 1.0))
            # Move back
            self.move_mouse(current_x, current_y)
            
        elif behavior == 'small_scroll':
            # Small random scroll
            scroll_amount = random.randint(-200, 200)
            self.scroll_page(amount=scroll_amount)
    
    def simulate_reading(self, word_count, max_time=30):
        """
        Simulate reading content with natural scrolling and pauses
        
        Args:
            word_count: Approximate number of words in the content
            max_time: Maximum time to spend reading regardless of content length
        """
        # Calculate base reading time based on reading speed (WPM)
        base_reading_time = (word_count / self.reading_speed_wpm) * 60
        
        # Add variability to reading time
        reading_time = base_reading_time * random.uniform(0.8, 1.2)
        
        # Cap reading time
        reading_time = min(reading_time, max_time)
        
        logging.info(f"Reading {word_count} words for {reading_time:.2f} seconds")
        
        # Break reading time into segments with scrolling
        time_elapsed = 0
        while time_elapsed < reading_time:
            # Read for a segment
            segment_time = random.uniform(2, 8)
            segment_time = min(segment_time, reading_time - time_elapsed)
            time.sleep(segment_time)
            time_elapsed += segment_time
            
            # Occasional scrolling between reading segments
            if time_elapsed < reading_time and random.random() < 0.7:
                # Scroll amount depends on time spent reading (simulates progress)
                progress = time_elapsed / reading_time
                scroll_amount = int(300 * random.uniform(0.8, 1.2))
                self.scroll_page(amount=scroll_amount)
        
        self.last_action_time = time.time()

# Example usage
if __name__ == "__main__":
    # Set up human simulation
    human = HumanSimulation()
    
    # Demo typing with realistic patterns
    human.type_text("This is a demonstration of human-like typing patterns. It includes typos and corrections.")
    
    # Demo mouse movement
    screen_width, screen_height = pyautogui.size()
    target_x = random.randint(100, screen_width - 100)
    target_y = random.randint(100, screen_height - 100)
    human.move_mouse(target_x, target_y)
    
    # Demo clicking
    human.click()
    
    # Demo scrolling
    human.scroll_page(content_length=200)  # Simulate reading ~200 words
    
    # Demo idle behavior
    human.random_idle_behavior()