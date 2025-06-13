"""Main entry point for the refactored Doc-MCP application."""

import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.ui.app import main

if __name__ == "__main__":
    main()
