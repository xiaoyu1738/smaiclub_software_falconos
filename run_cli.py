#!/usr/bin/env python3
import sys
import os

# Ensure src is in python path
sys.path.insert(0, os.path.abspath("src"))

from falcon.cli.main import run

if __name__ == "__main__":
    run()
