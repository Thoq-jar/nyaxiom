#!/usr/bin/env python3

import subprocess
from pathlib import Path

NAME = "axiom"
PATH = "/home/axiom"
SERVICE_PATH = "/etc/systemd/system/axiomd.service"


BANNER: str = """
⠀⠀⠀⠀⢐⡝⠛⢦⠀⠀⠘⠛⢦⡀⢀⣀⢀⣴⡯⠓⠀⣀⠔⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣠⠚⠁⠀⠀⠑⣣⢶⣿⣶⣿⣿⠿⢿⣥⣶⡛⠛⠰⢠⣀⠀⠀⠀⠀⠀⠀
⠀⠀⠈⠉⠀⣷⣶⡤⠞⣵⡿⢛⡼⠛⣭⢟⣆⠙⢿⡛⣿⣢⣀⠘⠷⣄⢀⣠⣤⠀
⠀⠀⠀⠀⠤⢾⡟⢁⡜⠁⠠⠍⠀⠀⡈⠈⠚⣂⠈⢷⢌⣯⢻⡝⣳⣼⣯⢽⡟⠀
⠀⠀⠀⠀⣠⡞⣴⠊⡄⢠⡏⠀⠀⡄⣇⢆⠀⠈⢧⡈⢧⣻⡷⣽⣾⣿⣷⣼⣦⠀
⠀⠀⣴⣾⣿⣭⡇⢼⣰⣯⣿⠀⠀⡇⣿⡘⣆⢰⣾⣿⣦⣻⣿⣮⣿⣿⣿⣿⣿⠀
⠀⠠⠿⣻⢿⣿⡃⢰⠿⣿⢹⣆⢀⣿⠋⣷⠻⣷⡁⠺⣿⣧⣷⡶⠻⢻⣽⣟⠃⠱
⠀⠀⢰⣿⢿⣟⣍⢏⠾⢸⣶⠉⢸⡿⣸⠈⢻⣵⣷⣄⡛⡎⢪⣯⣳⣌⢹⡇⠀⢀
⠀⢀⣿⣵⡿⢿⣼⣟⢻⣷⣾⣷⡀⣧⢹⡀⠀⠙⠳⡿⣷⢱⢸⢏⢿⡿⣮⡀⠀⠈
⠀⢨⣿⣿⣹⡎⡷⣏⠸⣿⠏⠈⠻⣿⠆⠷⠾⠿⡶⣶⡞⣼⢸⣌⠻⢿⣿⣄⡶⠠
⠀⣾⢿⡿⢻⣇⡇⢿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⡟⣽⡇⡇⢫⣧⣸⣿⠟⠿⣆
⠘⠃⠈⠁⠈⣽⢱⣈⢱⣄⠀⠶⠒⠂⡄⠀⣠⢾⣿⣣⡏⣛⣹⣦⣿⣿⣻⢿⣆⠀
⠀⠀⠀⠀⣀⣽⡶⠿⠍⠘⢻⣆⣘⣋⣤⠴⢛⣵⡿⢻⣷⡿⣵⠀⣿⣿⠟⠀⠙⠀
⢀⡲⡼⠏⠉⣾⠇⠀⠀⣠⡞⢁⣿⡿⣾⣿⠾⢟⡿⢸⣿⠀⠙⣧⣾⠀⠀⠀⠀⠀
⠬⠥⠤⠐⣲⣿⣆⠀⠀⠸⣄⡬⠙⣁⢽⠙⠦⣩⣅⠀⠱⣄⠞⠤⠩⠄⠀⠀⠀⠀
"""


class Ascii:
    PINK = "\x1b[38;5;206m"
    BOLD = "\x1b[1m"
    RESET = "\x1b[0m"


print(Ascii.PINK + BANNER + Ascii.RESET)


def log(message: str) -> None:
    print(f"{Ascii.BOLD}{Ascii.PINK}AXIOM:{Ascii.RESET} {message}")


def run(cmd: list):
    log(f"running: {cmd}")

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pass


def uninstall() -> None:
    log("stopping and disabling axiomd service...")
    run(["sudo", "systemctl", "stop", "axiomd"])
    run(["sudo", "systemctl", "disable", "axiomd"])

    if Path(SERVICE_PATH).exists():
        log("removing service file...")
        run(["sudo", "rm", SERVICE_PATH])
        run(["sudo", "systemctl", "daemon-reload"])

    log("removing user and home directory...")
    run(["sudo", "userdel", "-r", NAME])

    log("cleaning git safe directory config...")
    run(["sudo", "git", "config", "--global", "--unset-all", "safe.directory", PATH])

    log("uninstall complete!")


if __name__ == "__main__":
    uninstall()
