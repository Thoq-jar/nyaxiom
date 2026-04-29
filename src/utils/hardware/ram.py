import subprocess


def linux_ram_used() -> int:
    linux_used_memory_command = "free -b | grep Mem | awk '{print $3}'"
    linux_command_output = subprocess.check_output(
        linux_used_memory_command, shell=True
    )
    used_memory_bytes = int(linux_command_output.decode("utf-8").strip())
    return used_memory_bytes


def macos_ram_used() -> int:
    macos_used_memory_command = "vm_stat | perl -ne '/page size of (\\d+)/ && ($page_size=$1); /Pages (active|wired down|occupied by compressor):\\s+(\\d+)/ && ($used_pages+=$2); END {print $used_pages * $page_size}'"
    macos_command_output = subprocess.check_output(
        macos_used_memory_command, shell=True
    )
    used_memory_bytes = int(macos_command_output.decode("utf-8").strip())
    return used_memory_bytes


def windows_ram_used() -> int:
    windows_used_memory_command = 'powershell "(Get-CimInstance Win32_OperatingSystem).TotalVisibleMemorySize - (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"'
    windows_command_output = subprocess.check_output(
        windows_used_memory_command, shell=True
    )
    used_memory_kilobytes = int(windows_command_output.decode("utf-8").strip())
    used_memory_bytes = used_memory_kilobytes * 1024
    return used_memory_bytes


async def get_ram_usage() -> int:
    import src.utils.misc.nyaplatform as nyaplatform

    platform_type = nyaplatform.get_os()
    match platform_type:
        case nyaplatform.Platform.LINUX:
            return linux_ram_used()
        case nyaplatform.Platform.MACOS:
            return macos_ram_used()
        case nyaplatform.Platform.WINDOWS:
            return windows_ram_used()

    return 0
