#!/usr/bin/env python
"""
Simple entry point for vision functionality.
"""

if __name__ == "__main__":
    # This imports the main function from the src module
    from src.vision_main import main
    import sys
    sys.exit(main())