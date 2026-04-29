from quart import Blueprint

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
