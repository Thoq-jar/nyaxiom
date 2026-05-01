import os
from pathlib import Path


def read_dir_if_exists(dir: Path) -> list[Path]:
    if not os.path.exists(dir):
        return []

    files: list[Path] = []
    for file in dir.rglob("*"):
        files.append(file)

    return files
