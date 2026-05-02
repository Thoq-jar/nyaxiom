#!/usr/bin/env python3

import subprocess
from pathlib import Path

NAME = "axiom"
PATH = "/home/axiom"
SERVICE_PATH = "/etc/systemd/system/axiomd.service"


def run(cmd: list):
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pass


def uninstall() -> None:
    print(f"Stopping and disabling {NAME}d service...")
    run(["sudo", "systemctl", "stop", "axiomd"])
    run(["sudo", "systemctl", "disable", "axiomd"])

    if Path(SERVICE_PATH).exists():
        print("Removing service file...")
        run(["sudo", "rm", SERVICE_PATH])
        run(["sudo", "systemctl", "daemon-reload"])

    print("Removing user and home directory...")
    run(["sudo", "userdel", "-r", NAME])

    print("Cleaning git safe directory config...")
    run(["sudo", "git", "config", "--global", "--unset-all", "safe.directory", PATH])

    print("Uninstall complete!")


if __name__ == "__main__":
    uninstall()
