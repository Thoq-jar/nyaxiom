from quart import (
    Blueprint,
    render_template,
    request,
    send_from_directory,
    redirect,
    url_for,
)
from datetime import datetime
import os
from src.features.weather import get_weather_data
from src.db.model import FetchTask
from src.db.db import db

main_bp = Blueprint("main", __name__)

NAV_ITEMS = [
    {"name": "Home", "url": "/", "icon": "/static/image/icons/home.svg"},
    {"name": "CPU", "url": "/cpu", "icon": "/static/image/icons/cpu.svg"},
    {"name": "Logs", "url": "/logs", "icon": "/static/image/icons/browse.svg"},
    {"name": "Item4", "url": "#", "icon": None},
]


@main_bp.context_processor
def inject_globals():
    task = FetchTask.query.filter_by(task_name="dashboard").first()
    interval = task.update_interval if task else 3
    return {
        "nav_items": NAV_ITEMS,
        "active_path": request.path,
        "update_interval": interval,
    }


@main_bp.get("/")
async def index():
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif 12 <= hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    weather = await get_weather_data()
    today_date = datetime.now().strftime("%b %d")

    return await render_template(
        "home.jinja2",
        title="Home",
        greeting=greeting,
        location=weather["location"],
        current_temp=weather["temp"],
        current_icon=weather["icon_url"],
        forecast=weather["forecast"],
        stats=[{"title": "CPU", "percentage": 0}, {"title": "RAM", "percentage": 0}],
        today_date=today_date,
    )


@main_bp.get("/settings")
async def settings():
    task = FetchTask.query.filter_by(task_name="dashboard").first()
    return await render_template(
        "settings.jinja2",
        title="Settings",
        interval=task.update_interval if task else 3,
    )


@main_bp.get("/logs")
async def logs():
    return await render_template("logs.jinja2", title="Logs")


@main_bp.get("/cpu")
async def cpu():
    from src.utils.hardware.cpu import get_by_core_cpu_usage

    cores = await get_by_core_cpu_usage()
    stats = []
    for core_dict in cores:
        for core_id, usage in core_dict.items():
            stats.append({"title": f"Core {core_id}", "percentage": usage})

    return await render_template(
        "cpu.jinja2",
        title="CPU",
        stats=stats,
    )


@main_bp.post("/settings")
async def update_settings():
    form = await request.form
    interval = form.get("interval", type=int)
    if interval:
        task = FetchTask.query.filter_by(task_name="dashboard").first()
        if task:
            task.update_interval = interval
            db.session.commit()
    return redirect(url_for("main.settings"))


@main_bp.route("/favicon.svg")
async def favicon():
    return await send_from_directory(os.getcwd(), "favicon.svg")
