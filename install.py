#!/usr/bin/env python3

import subprocess
from pathlib import Path

DEPS = ["python3.13", "git"]
NAME = "axiom"
PATH = "/home/axiom"


def check_command(command: str) -> bool:
    return subprocess.run([command, "--version"], capture_output=True).returncode == 0


def find_exe(command: str) -> str:
    result = subprocess.run(["which", command], capture_output=True, text=True)
    return result.stdout.strip()


def check_deps() -> None:
    for dep in DEPS:
        if not check_command(dep):
            print(f"Error: {dep} is not installed")
            exit(1)
        else:
            print(f"Found: {dep} ({find_exe(dep)})")


def parse_os_release(content: str, key: str) -> str:
    for line in content.splitlines():
        if line.startswith(key + "="):
            return line.split("=")[1].strip()
    return ""


def get_os_release() -> str:
    release = Path("/etc/os-release")
    with open(release, "r") as file:
        content = file.read()
        id_like = parse_os_release(content, "ID_LIKE")
        if id_like == "":
            return parse_os_release(content, "ID").strip()

        return id_like.strip()


def check_os() -> None:
    operating_system = get_os_release()
    print(f"Detected OS: {operating_system}")
    if operating_system != "arch":
        print(
            "Unsupported OS: only Arch Linux is supported at the moment, Debian is planned."
        )
        exit(1)
    else:
        print("     > OS is supported")


def add_user(username: str, password: str):
    print(f"Creating user '{username}' with password '{password}'...")

    try:
        subprocess.run(["sudo", "useradd", "-p", password, username])
    except Exception as exception:
        print(f"    > Failed to add user: {exception}")
        exit(1)
    print(f"     > User '{username}' created successfully")


def setup_user_stage1() -> None:
    import getpass

    current_user = getpass.getuser()
    print(f"Assigning {PATH} to {current_user} for installation...")

    subprocess.run(["sudo", "mkdir", "-p", PATH], check=True)
    subprocess.run(
        ["sudo", "chown", "-R", f"{current_user}:{current_user}", PATH], check=True
    )


def setup_user_stage2() -> None:
    import glob
    import os

    subprocess.run(["sudo", "chown", "-R", f"{NAME}:{NAME}", PATH], check=True)
    subprocess.run(["sudo", "chmod", "755", PATH], check=True)
    bin_path = f"{PATH}/bin"
    venv_bin = f"{PATH}/.venv/bin"
    subprocess.run(["sudo", "chmod", "-R", "755", bin_path], check=True)
    for file in glob.glob(f"{bin_path}/*"):
        subprocess.run(["sudo", "chmod", "+x", file], check=True)
    if os.path.exists(venv_bin):
        subprocess.run(["sudo", "chmod", "-R", "755", venv_bin], check=True)


def clone_repo() -> None:
    import os

    repo_url = "https://github.com/Thoq-jar/nyaxiom.git"
    subprocess.run(
        ["git", "config", "--global", "--add", "safe.directory", PATH], check=True
    )
    if os.path.exists(os.path.join(PATH, ".git")):
        subprocess.run(["git", "-C", PATH, "pull"], check=True)
    else:
        subprocess.run(["git", "clone", repo_url, PATH], check=True)


def setup_venv() -> None:
    python = find_exe("python3.13") or "/usr/bin/python3.13"
    subprocess.run(["sudo", "chown", "-R", f"{NAME}:{NAME}", PATH], check=True)
    subprocess.run(
        ["sudo", "-u", NAME, python, "-m", "venv", f"{PATH}/.venv"], check=True
    )
    subprocess.run(
        ["sudo", "-u", NAME, f"{PATH}/.venv/bin/pip", "install", PATH], check=True
    )


def register_service() -> None:
    import subprocess

    print("Registering service...")
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
    print("     > Service registered successfully")


def main() -> None:
    check_deps()
    check_os()
    add_user(NAME, NAME)
    setup_user_stage1()
    clone_repo()
    setup_venv()
    setup_user_stage2()
    register_service()

    print("Installation complete!")
    print(" | To start Axiom, run: `sudo systemctl start axiomd`")
    print(" | To enable Axiom on boot, run: `sudo systemctl enable axiomd`")
    print(" | To do both, run: `sudo systemctl enable --now axiomd`")


if __name__ == "__main__":
    main()
