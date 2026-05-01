from pathlib import Path
from quart import Blueprint
from src.features.logs import read_log_dirs, read_log

api_bp = Blueprint("api", __name__)


@api_bp.get("/hardware/cpu/usage")
async def get_cpu_usage():
    from src.utils.hardware.cpu import get_cpu_usage

    return {"usage": await get_cpu_usage()}


@api_bp.get("/hardware/ram/usage")
async def get_ram_usage():
    from src.utils.hardware.ram import get_ram_usage

    total = 16 * 1024 * 1024 * 1024
    used = await get_ram_usage()
    percentage = (used / total) * 100

    return {"usage": round(percentage, 1)}


@api_bp.get("/os/logs/retrieve")
async def retrieve_logs():
    log_paths: list[Path] = read_log_dirs()

    log_data: list[dict[str, str]] = []
    for log_path in log_paths:
        if log_path.suffix in [".gz", ".zip", ".1"]:
            continue

        content: str = read_log(log_path)
        log_data.append(
            {
                "id": str(log_path),
                "name": log_path.name,
                "content": content,
            }
        )

    return log_data
