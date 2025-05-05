#!/usr/bin/env python
"""
Simple wrapper script to run the Qwen interface.
"""
import sys
import subprocess

def main():
    """Run the Qwen interface module."""
    args = sys.argv[1:]
    cmd = [sys.executable, "-m", "src.qwen_main"] + args
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()