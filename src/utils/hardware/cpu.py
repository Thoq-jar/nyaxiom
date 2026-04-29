def linux_cpu() -> float:
    import time

    def read_stats():
        with open("/proc/stat", "r") as file:
            parts = file.readline().split()
            idle_time = float(parts[4]) + float(parts[5])
            total_time = sum(float(x) for x in parts[1:])
            return idle_time, total_time

    idle1, total1 = read_stats()
    time.sleep(1)
    idle2, total2 = read_stats()

    idle_delta = idle2 - idle1
    total_delta = total2 - total1

    usage = 100 * (1.0 - idle_delta / total_delta)
    return usage


def macos_cpu() -> float:
    import subprocess

    cmd = "top -l 1 | grep 'CPU usage' | awk '{print $3}' | cut -d'%' -f1"
    usage: str = subprocess.check_output(cmd, shell=True).decode().strip()
    return float(usage)


def windows_cpu() -> float:
    import subprocess

    cmd = "wmic cpu get loadpercentage"
    output = subprocess.check_output(cmd, shell=True).decode()
    usage = output.split("\n")[1].strip()
    return float(usage)


async def get_cpu_usage() -> float:
    import src.utils.misc.nyaplatform as nyaplatform

    platform = nyaplatform.get_os()
    match platform:
        case nyaplatform.Platform.LINUX:
            return linux_cpu()
        case nyaplatform.Platform.MACOS:
            return macos_cpu()
        case nyaplatform.Platform.WINDOWS:
            return windows_cpu()

    return 0.0
