from pathlib import Path

from quart import Blueprint, redirect, request, url_for

from src.db.db import db
from src.db.model import FetchTask, SearchEngine, ShowWeather
from src.features.logs import read_log, read_log_dirs
from src.utils.misc.units import GIGABYTE

api_bp = Blueprint("api", __name__)


@api_bp.get("/hardware/cpu/usage")
async def get_cpu_usage():
    from src.utils.hardware.cpu import get_cpu_usage

    return {"usage": await get_cpu_usage()}


@api_bp.get("/hardware/cpu/core_usage")
async def get_core_cpu_usage():
    from src.utils.hardware.cpu import get_by_core_cpu_usage

    return await get_by_core_cpu_usage()


@api_bp.get("/hardware/ram/usage")
async def get_ram_usage():
    from src.utils.hardware.ram import get_ram_usage

    total = 16 * GIGABYTE
    used = await get_ram_usage()
    percentage = (used / total) * 100

    return {"usage": round(percentage, 1)}


@api_bp.get("/hardware/ram/free")
async def get_free_ram():
    from src.utils.hardware.ram import get_free_memory

    free = await get_free_memory()
    return {"free": free}


@api_bp.get("/hardware/ram/free_used")
async def get_free_used_ram():
    from src.utils.hardware.ram import get_free_memory, get_ram_usage, get_total_memory

    total = await get_total_memory() * GIGABYTE
    free = await get_free_memory() * GIGABYTE
    used = await get_ram_usage() * GIGABYTE
    percentage_used = (used / total) * 100
    percentage_free = (free / total) * 100
    return {"free": percentage_free, "used": percentage_used}


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


@api_bp.post("/settings")
async def update_settings():
    form = await request.form
    interval = form.get("interval", type=int)
    if interval:
        task = FetchTask.query.filter_by(task_name="dashboard").first()
        if task:
            task.update_interval = interval
            db.session.commit()

    show_weather = form.get("weather") == "on"
    if show_weather is not None:
        task = ShowWeather.query.filter_by(task_name="dashboard").first()
        if task:
            task.checked = show_weather
            db.session.commit()

    search_engine = form.get("search-engine")
    if search_engine:
        task = SearchEngine.query.filter_by(task_name="dashboard").first()
        if task:
            task.engine = search_engine
            db.session.commit()

    return redirect(url_for("main.settings"))
