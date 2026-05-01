# todo: maybe support windows

import getpass
import gzip
from src.utils.misc.dirutil import read_dir_if_exists
from pathlib import Path


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
        Path("/var/log/syslog"),
        Path("/var/log/messages"),
        Path("/var/log/auth.log"),
        Path("/var/log/secure"),
        Path("/var/log/kern.log"),
        Path("/var/log/cron"),
    ]
    macos_dirs: list[Path] = [
        Path(f"/Users/{username}/Library/Logs"),
        Path("/Library/Logs"),
        Path("/var/db/diagnostics"),
    ]

    logs: list[Path] = []

    for path in linux_paths:
        if path.exists() and path.is_file():
            logs.append(path)

    for directory in macos_dirs:
        files: list[Path] = read_dir_if_exists(directory)
        for file_path in files:
            if file_path.is_file() and "log" in file_path.name.lower():
                logs.append(file_path)

    return logs
