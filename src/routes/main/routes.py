from quart import Blueprint, render_template, request, send_from_directory
from datetime import datetime
import os
from src.features.weather import get_weather_data

main_bp = Blueprint("main", __name__)

NAV_ITEMS = [
    {"name": "Home", "url": "/", "icon": "/static/image/home.svg"},
    {"name": "Item2", "url": "#", "icon": None},
    {"name": "Item3", "url": "#", "icon": None},
    {"name": "Item4", "url": "#", "icon": None},
]


@main_bp.context_processor
def inject_globals():
    return {"nav_items": NAV_ITEMS, "active_path": request.path, "update_interval": 3}


@main_bp.get("/")
async def index():
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning!"
    elif 12 <= hour < 18:
        greeting = "Good afternoon!"
    else:
        greeting = "Good evening!"

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
        today_date=today_date,
    )


@main_bp.get("/settings")
async def settings():
    return await render_template("settings.jinja2", title="Settings")


@main_bp.route("/favicon.svg")
async def favicon():
    return await send_from_directory(os.getcwd(), "favicon.svg")
