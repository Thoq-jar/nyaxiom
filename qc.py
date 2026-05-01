#!.venv/bin/python

import subprocess
import sys


def run_command(command):
    print(f"Running: {' '.join(command)}...")
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"Error: {command[0]} failed.")
        sys.exit(result.returncode)


if __name__ == "__main__":
    run_command(["ruff", "format", "."])
    run_command(["ruff", "check", ".", "--fix"])
    run_command(["ty", "check", "."])

    print("\nAll checks passed!")
