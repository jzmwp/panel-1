"""Run database seed."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.seed.seed_data import run_seed

if __name__ == "__main__":
    run_seed()
