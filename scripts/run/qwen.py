#!/usr/bin/env python
"""
Convenience script to run Qwen interface.
"""

if __name__ == "__main__":
    # Add the project root to path to allow package imports
    import sys
    import os
    
    # Get the absolute path to the project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../.."))
    
    # Add the project root to sys.path
    sys.path.insert(0, project_root)
    
    # Import the main function
    from src.qwen_main import main
    sys.exit(main())