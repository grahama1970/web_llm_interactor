#!/usr/bin/env python
"""
Simple entry point for Qwen CLI.
"""

if __name__ == "__main__":
    # This imports the main function from the src module
    from src.qwen_main import main
    import sys
    sys.exit(main())