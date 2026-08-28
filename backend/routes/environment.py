from fastapi import APIRouter
from ..services.weather_service import fetch_environmental_data
from ..services.terrain_service import get_terrain_info

router = APIRouter()

@router.get("/environment/{lat}/{lon}")
async def get_environment_info(lat: float, lon: float, location_name: str = "Selected Location"):
    env = await fetch_environmental_data(lat, lon)
    slope, elevation, _ = get_terrain_info(location_name, lat, lon)
    env.slope = slope
    env.elevation = elevation
    return env