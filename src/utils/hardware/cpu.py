import subprocess
import time
import src.utils.misc.nyaplatform as nyaplatform


def linux_cpu_per_core() -> list[dict[str, float]]:
    def read_core_stats():
        core_data = []
        with open("/proc/stat", "r") as file:
            for line in file:
                if line.startswith("cpu") and not line.startswith("cpu "):
                    parts = line.split()
                    core_id = parts[0].replace("cpu", "")
                    idle_time = float(parts[4]) + float(parts[5])
                    total_time = sum(float(x) for x in parts[1:])
                    core_data.append(
                        {"id": core_id, "idle": idle_time, "total": total_time}
                    )
        return core_data

    start_stats = read_core_stats()
    time.sleep(1)
    end_stats = read_core_stats()
    usage_list = []
    for start, end in zip(start_stats, end_stats):
        idle_delta = end["idle"] - start["idle"]
        total_delta = end["total"] - start["total"]
        core_usage = (
            100.0 * (1.0 - idle_delta / total_delta) if total_delta > 0 else 0.0
        )
        usage_list.append({start["id"]: round(core_usage, 2)})
    return usage_list


def macos_cpu_per_core() -> list[dict[str, float]]:
    import ctypes

    try:
        lib = ctypes.CDLL("/usr/lib/libSystem.B.dylib")

        PROCESSOR_CPU_LOAD_INFO = 2

        class processor_cpu_load_info(ctypes.Structure):
            _fields_ = [("cpu_ticks", ctypes.c_uint32 * 4)]

        host_processor_info = lib.host_processor_info
        host_processor_info.argtypes = [
            ctypes.c_uint,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_uint),
            ctypes.POINTER(ctypes.POINTER(processor_cpu_load_info)),
            ctypes.POINTER(ctypes.c_uint),
        ]

        mach_host_self = lib.mach_host_self
        mach_host_self.restype = ctypes.c_uint

        vm_deallocate = lib.vm_deallocate
        vm_deallocate.argtypes = [ctypes.c_uint, ctypes.c_void_p, ctypes.c_size_t]

        mach_task_self_func = lib.mach_task_self
        mach_task_self_func.restype = ctypes.c_uint

        def get_ticks():
            host = mach_host_self()
            cpu_count = ctypes.c_uint(0)
            cpu_info = ctypes.POINTER(processor_cpu_load_info)()
            info_count = ctypes.c_uint(0)

            res = host_processor_info(
                host,
                PROCESSOR_CPU_LOAD_INFO,
                ctypes.byref(cpu_count),
                ctypes.byref(cpu_info),
                ctypes.byref(info_count),
            )
            if res != 0:
                return []

            ticks = []
            for index in range(cpu_count.value):
                ticks_now = cpu_info[index].cpu_ticks
                ticks.append((ticks_now[0], ticks_now[1], ticks_now[2], ticks_now[3]))

            vm_deallocate(
                mach_task_self_func(),
                ctypes.cast(cpu_info, ctypes.c_void_p),
                info_count.value * ctypes.sizeof(ctypes.c_int),
            )
            return ticks

        ticks1 = get_ticks()
        if not ticks1:
            return []
        time.sleep(0.2)
        ticks2 = get_ticks()

        usage_list = []
        for index, (start, end) in enumerate(zip(ticks1, ticks2)):
            deltas = [e - s for s, e in zip(start, end)]
            total = sum(deltas)
            if total > 0:
                idle = deltas[2]
                usage = 100.0 * (1.0 - idle / total)
            else:
                usage = 0.0
            usage_list.append({str(index): round(usage, 2)})

        return usage_list
    except Exception:
        return []


def windows_cpu_per_core() -> list[dict[str, float]]:
    cmd = "wmic cpu get loadpercentage /all"
    output = subprocess.check_output(cmd, shell=True).decode().splitlines()
    usage_list = []
    core_idx = 0
    for line in output:
        clean = line.strip()
        if clean and clean.isdigit():
            usage_list.append({str(core_idx): float(clean)})
            core_idx += 1
    return usage_list


async def get_by_core_cpu_usage() -> list[dict[str, float]]:
    platform = nyaplatform.get_os()
    match platform:
        case nyaplatform.Platform.LINUX:
            return linux_cpu_per_core()
        case nyaplatform.Platform.MACOS:
            return macos_cpu_per_core()
        case nyaplatform.Platform.WINDOWS:
            return windows_cpu_per_core()
    return []


def linux_cpu() -> float:
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
    return 100 * (1.0 - idle_delta / total_delta) if total_delta > 0 else 0.0


def macos_cpu() -> float:
    cmd = "sysctl -n vm.loadavg"
    output = subprocess.check_output(cmd, shell=True).decode()
    load = float(output.split()[1])
    count = int(subprocess.check_output("sysctl -n hw.ncpu", shell=True).decode())
    usage = (load / count) * 100
    return round(min(usage, 100.0), 2)


def windows_cpu() -> float:
    cmd = "wmic cpu get loadpercentage"
    output = subprocess.check_output(cmd, shell=True).decode()
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) > 1:
        return float(lines[1])
    return 0.0


async def get_cpu_usage() -> float:
    platform = nyaplatform.get_os()
    match platform:
        case nyaplatform.Platform.LINUX:
            return linux_cpu()
        case nyaplatform.Platform.MACOS:
            return macos_cpu()
        case nyaplatform.Platform.WINDOWS:
            return windows_cpu()
    return 0.0
