#!/usr/bin/env python3
"""Quick start script for ETL pipeline."""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from etl.pipeline import main

if __name__ == "__main__":
    main()
