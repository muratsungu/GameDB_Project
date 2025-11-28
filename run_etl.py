#!/usr/bin/env python3
"""ETL pipeline entry point."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from etl.pipeline import main

if __name__ == "__main__":
    main()
