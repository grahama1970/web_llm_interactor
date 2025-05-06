import unittest
import subprocess
import json
import os
import sys
import time
from pathlib import Path

class TestCliIntegration(unittest.TestCase):
    """
    Integration tests for the web-llm-interactor CLI.
    These tests require an open Chrome tab with https://chat.qwen.ai/
    """
    
    def setUp(self):
        self.cli_module = "web_llm_interactor.cli"
        
        # Check if Chrome is open with Qwen
        result = subprocess.run(
            ["osascript", "-e", 'tell application "Google Chrome" to get URL of active tab of first window'],
            capture_output=True,
            text=True
        )
        if "qwen.ai" not in result.stdout.lower():
            print("\nWARNING: Please open https://chat.qwen.ai/ in Chrome before running these tests.")
            print("Output:", result.stdout)
            time.sleep(3)
    
    def test_basic_question(self):
        """Test a simple question to Qwen with the default JSON fields."""
        
        # Run the CLI command through Python module
        result = subprocess.run(
            [sys.executable, "-m", self.cli_module, "ask", 
             "What is the capital of Arizona?", 
             "--timeout", "45"],
            capture_output=True,
            text=True
        )
        
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        # Check if we got a successful result
        self.assertEqual(result.returncode, 0, f"CLI failed with error: {result.stderr}")
        
        # Extract the JSON part from the output
        json_start = result.stdout.find('{')
        json_part = result.stdout[json_start:]
        
        # Verify JSON response has required fields
        try:
            response_json = json.loads(json_part)
            self.assertIn("question", response_json)
            self.assertIn("thinking", response_json)
            self.assertIn("answer", response_json)
            
            # Basic content validation
            self.assertTrue(len(response_json["answer"]) > 10)
            self.assertTrue("Phoenix" in response_json["answer"])
            
            print(f"\nSuccessfully parsed JSON response from Qwen:")
            print(f"Question: {response_json['question']}")
            print(f"Answer begins: {response_json['answer'][:100]}...")
            print(f"Thinking begins: {response_json['thinking'][:100]}...")
            
        except json.JSONDecodeError:
            self.fail(f"Failed to parse JSON from output: {json_part}")
    
    def test_custom_fields(self):
        """Test using custom fields in the JSON response."""
        
        # Run the CLI command with custom fields
        result = subprocess.run(
            [sys.executable, "-m", self.cli_module, "ask", 
             "What is the capital of New Mexico?", 
             "--fields", "question,answer",
             "--timeout", "45"],
            capture_output=True,
            text=True
        )
        
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        # Check if we got a successful result
        self.assertEqual(result.returncode, 0, f"CLI failed with error: {result.stderr}")
        
        # Extract the JSON part from the output
        json_start = result.stdout.find('{')
        json_part = result.stdout[json_start:]
        
        # Verify JSON response has required fields
        try:
            response_json = json.loads(json_part)
            self.assertIn("question", response_json)
            self.assertIn("answer", response_json)
            
            # Basic content validation
            self.assertTrue(len(response_json["answer"]) > 10)
            self.assertTrue("Santa Fe" in response_json["answer"])
            
            print(f"\nSuccessfully parsed JSON response with custom fields:")
            print(f"Question: {response_json['question']}")
            print(f"Answer begins: {response_json['answer'][:100]}...")
            
        except json.JSONDecodeError:
            self.fail(f"Failed to parse JSON from output: {json_part}")


if __name__ == "__main__":
    unittest.main()