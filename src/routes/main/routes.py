import os
from datetime import datetime

from quart import (
    Blueprint,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from src.db.db import db
from src.db.model import FetchTask, SearchEngine, ShowWeather
from src.features.weather import get_weather_data

main_bp = Blueprint("main", __name__)

NAV_ITEMS = [
    {"name": "Home", "url": "/", "icon": "/static/image/icons/home.svg"},
    {"name": "CPU", "url": "/cpu", "icon": "/static/image/icons/cpu.svg"},
    {"name": "Memory", "url": "/memory", "icon": "/static/image/icons/memory.svg"},
    {"name": "Logs", "url": "/logs", "icon": "/static/image/icons/browse.svg"},
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
    from src.utils.hardware.cpu import get_cpu_usage
    from src.utils.hardware.ram import get_percentage_used

    show_weather = (
        ShowWeather.query.filter_by(task_name="dashboard").first().checked or False
    )
    search_engine = (
        SearchEngine.query.filter_by(task_name="dashboard")
        .first()
        .engine.replace("%s", "")
    )

    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif 12 <= hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    weather = {}
    if show_weather:
        weather = await get_weather_data()

    today_date = datetime.now().strftime("%b %d")

    if show_weather:
        return await render_template(
            "home.jinja2",
            title="Home",
            greeting=greeting,
            location=weather["location"],
            current_temp=weather["temp"],
            current_icon=weather["icon_url"],
            forecast=weather["forecast"],
            show_weather=show_weather,
            engine=search_engine,
            stats=[
                {"title": "CPU", "percentage": round(await get_cpu_usage())},
                {"title": "RAM", "percentage": round(await get_percentage_used())},
            ],
            today_date=today_date,
        )

    return await render_template(
        "home.jinja2",
        title="Home",
        greeting=greeting,
        location="Weather disabled",
        current_temp="Weather disabled",
        current_icon="Weather disabled",
        forecast="Weather disabled",
        show_weather=show_weather,
        engine=search_engine,
        stats=[
            {"title": "CPU", "percentage": round(await get_cpu_usage())},
            {"title": "RAM", "percentage": round(await get_percentage_used())},
        ],
        today_date=today_date,
    )


@main_bp.get("/settings")
async def settings():
    fetch_task = FetchTask.query.filter_by(task_name="dashboard").first()
    show_weather = ShowWeather.query.filter_by(task_name="dashboard").first()
    search_engine = SearchEngine.query.filter_by(task_name="dashboard").first()
    return await render_template(
        "settings.jinja2",
        title="Settings",
        interval=fetch_task.update_interval if fetch_task else 3,
        weather=show_weather.checked if show_weather else True,
        search_engine=search_engine.engine if search_engine else None,
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
            usage = round(usage)
            stats.append({"title": f"Core {core_id}", "percentage": usage})

    return await render_template(
        "cpu.jinja2",
        title="CPU",
        stats=stats,
    )


@main_bp.get("/memory")
async def memory():
    from src.utils.hardware.ram import get_percent_free, get_percentage_used

    return await render_template(
        "memory.jinja2",
        title="Memory",
        stats=[
            {"title": "Free", "percentage": round(await get_percent_free())},
            {"title": "Used", "percentage": round(await get_percentage_used())},
        ],
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


@main_bp.route("/favicon.svg")
async def favicon():
    return await send_from_directory(os.getcwd(), "favicon.svg")
