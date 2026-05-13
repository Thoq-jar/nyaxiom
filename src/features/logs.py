# todo: maybe support windows

import getpass
import gzip
from pathlib import Path

from src.utils.misc.dirutil import read_dir_if_exists


def read_log(path: Path) -> str:
    if not path.exists():
        return ""

    if path.suffix != ".gz":
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return ""

    try:
        with gzip.open(path, "rb") as compressed_file:
            content_bytes: bytes = compressed_file.read()
            return content_bytes.decode(encoding="utf-8", errors="replace")
    except Exception:
        return "[Error decompressing log]"


def read_log_dirs():
    username: str = getpass.getuser()
    linux_paths: list[Path] = [
        Path("/var/log/"),
    ]
    macos_dirs: list[Path] = [
        Path(f"/Users/{username}/Library/Logs"),
        Path("/Library/Logs"),
        Path("/var/db/diagnostics"),
    ]

    logs: list[Path] = []

    for path in linux_paths:
        files: list[Path] = read_dir_if_exists(path)

        for file_path in files:
            try:
                if file_path.exists() and file_path.is_file():
                    logs.append(file_path)
            except Exception:
                continue

    for directory in macos_dirs:
        files: list[Path] = read_dir_if_exists(directory)
        for file_path in files:
            try:
                if file_path.is_file() and "log" in file_path.name.lower():
                    logs.append(file_path)
            except Exception:
                continue

    return logs
