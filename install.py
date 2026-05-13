#!/usr/bin/env python3

from pathlib import Path
from subprocess import CompletedProcess

DEPS: list[str] = ["python3.13", "git"]
NAME: str = "axiom"
PATH: str = "/home/axiom"
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


def run(
    cmd: list, capture_output: bool = False, text: bool = False, check: bool = False
) -> CompletedProcess:
    import subprocess

    log(f"running: {cmd}")
    try:
        return subprocess.run(
            cmd, check=check, capture_output=capture_output, text=text
        )
    except subprocess.CalledProcessError as exception:
        return subprocess.CompletedProcess(
            cmd, returncode=exception.returncode, stdout=None, stderr=None
        )


def check_command(command: str) -> bool:
    log(f"checking for {command}")
    return run([command, "--version"], capture_output=True).returncode == 0


def find_exe(command: str) -> str:
    log(f"finding {command}")
    result = run(["which", command], capture_output=True, text=True)
    return result.stdout.strip()


def check_deps() -> None:
    for dep in DEPS:
        if not check_command(dep):
            log(f"error: {dep} is not installed")
            exit(1)
        else:
            log(f"found: {dep} ({find_exe(dep)})")


def parse_os_release(content: str, key: str) -> str:
    log(f"parsing os release for {key}")
    for line in content.splitlines():
        if line.startswith(key + "="):
            return line.split("=")[1].strip()
    return ""


def get_os_release() -> str:
    log("getting os release")
    release = Path("/etc/os-release")
    with open(release, "r") as file:
        content = file.read()
        id_like = parse_os_release(content, "ID_LIKE")
        if id_like == "":
            return parse_os_release(content, "ID").strip()

        return id_like.strip()


def check_os() -> None:
    log("checking OS")
    operating_system = get_os_release()
    log(f"detected OS: {operating_system}")
    if operating_system != "arch":
        log(
            "unsupported OS: only Arch Linux is supported at the moment, Debian is planned."
        )
        exit(1)
    else:
        log("     > OS is supported")


def add_user(username: str, password: str):
    log(f"creating user '{username}' with password '{password}'...")

    try:
        run(["sudo", "useradd", "-p", password, username])
    except Exception as exception:
        log(f"    > failed to add user: {exception}")
        exit(1)
    log(f"     > user '{username}' created successfully")


def setup_user_stage1() -> None:
    import getpass

    log("setting up user stage 1")
    current_user = getpass.getuser()
    log(f"assigning {PATH} to {current_user} for installation...")

    run(["sudo", "mkdir", "-p", PATH], check=True)
    run(["sudo", "chown", "-R", f"{current_user}:{current_user}", PATH], check=True)


def setup_user_stage2() -> None:
    import glob
    import os

    log("setting up user stage 2")
    run(["sudo", "chown", "-R", f"{NAME}:{NAME}", PATH], check=True)
    run(["sudo", "chmod", "755", PATH], check=True)
    bin_path = f"{PATH}/bin"
    venv_bin = f"{PATH}/.venv/bin"
    run(["sudo", "chmod", "-R", "755", bin_path], check=True)
    for file in glob.glob(f"{bin_path}/*"):
        run(["sudo", "chmod", "+x", file], check=True)
    if os.path.exists(venv_bin):
        run(["sudo", "chmod", "-R", "755", venv_bin], check=True)


def clone_repo() -> None:
    import os

    log("cloning repo")
    repo_url = "https://github.com/Thoq-jar/nyaxiom.git"
    run(["git", "config", "--global", "--add", "safe.directory", PATH], check=True)
    if os.path.exists(os.path.join(PATH, ".git")):
        run(["git", "-C", PATH, "pull"], check=True)
    else:
        run(["git", "clone", repo_url, PATH], check=True)


def setup_venv() -> None:
    python = find_exe("python3.13") or "/usr/bin/python3.13"
    log("setting up venv")
    run(["sudo", "chown", "-R", f"{NAME}:{NAME}", PATH], check=True)
    run(["sudo", "-u", NAME, python, "-m", "venv", f"{PATH}/.venv"], check=True)
    run(["sudo", "-u", NAME, f"{PATH}/.venv/bin/pip", "install", PATH], check=True)


def register_service() -> None:
    import subprocess

    log("registering service...")
    subprocess.run(
        [
            "sudo",
            "cp",
            f"{PATH}/services/axiomd.service",
            "/etc/systemd/system/axiomd.service",
        ],
        check=True,
    )
    subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
    log("     > service registered successfully")


def main() -> None:
    check_deps()
    check_os()
    add_user(NAME, NAME)
    setup_user_stage1()
    clone_repo()
    setup_venv()
    setup_user_stage2()
    register_service()

    log("Installation complete!")
    log(" | To start Axiom, run: `sudo systemctl start axiomd`")
    log(" | To enable Axiom on boot, run: `sudo systemctl enable axiomd`")
    log(" | To do both, run: `sudo systemctl enable --now axiomd`")
    log(" | If you just updated, run: `sudo systemctl restart axiomd`")


if __name__ == "__main__":
    main()
