#!/usr/bin/env python
"""
Simple wrapper script to run the main CLI interface.
"""
import sys
import subprocess

def main():
    """Run the main CLI module."""
    args = sys.argv[1:]
    cmd = [sys.executable, "-m", "src.main"] + args
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()