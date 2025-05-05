#!/usr/bin/env python
"""
Simple entry point for main CLI.
"""

if __name__ == "__main__":
    # This imports the main function from the src module
    from src.main import main
    import sys
    sys.exit(main())