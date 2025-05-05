#!/usr/bin/env python
"""
Simple entry point for paste text functionality.
"""

if __name__ == "__main__":
    # This imports the main function from the src module
    from src.paste_text import main
    import sys
    sys.exit(main())