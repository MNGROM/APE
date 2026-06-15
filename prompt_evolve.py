#!/usr/bin/env python3
"""Compatibility wrapper for the refactored APE runner.

The implementation now lives in `run.py` and supporting modules. This file is
kept so older commands that call `python prompt_evolve.py ...` still work.
"""

from __future__ import annotations

from run import main


if __name__ == "__main__":
    main()
