import logging
from datetime import datetime

import httpx

from ..models.schemas import EnvironmentalData

logger = logging.getLogger(__name__)


def _fallback_data() -> EnvironmentalData:
    # Explicitly marked demo values so the UI can disclose when live weather
    # is unavailable. This keeps the SIH prototype demonstrable without
    # pretending the values are real observations.
    return EnvironmentalData(
        rainfall_1h=12.4,
        rainfall_3h=32.0,
        rainfall_24h=68.5,
        rainfall_intensity=12.4,
        soil_moisture=82.0,
        humidity=88.0,
        temperature=20.5,
        wind_speed=11.0,
        data_source="DEMO_FALLBACK"
    )


async def fetch_environmental_data(lat: float, lon: float) -> EnvironmentalData:
    """
    Fetch live weather from Open-Meteo.

    The API request includes one previous day so the last 24 hourly
    precipitation values are genuinely historical/recent values rather
    than the final 24 forecast values.
    """
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Latitude must be -90..90 and longitude must be -180..180.")

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": (
            "precipitation,relative_humidity_2m,temperature_2m,"
            "wind_speed_10m,soil_moisture_0_to_1cm"
        ),
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "past_days": 1,
        "forecast_days": 1,
        "timezone": "auto",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params=params,
            )
            response.raise_for_status()
            data = response.json()

        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        precipitation = hourly.get("precipitation", [])
        humidity_values = hourly.get("relative_humidity_2m", [])
        temperature_values = hourly.get("temperature_2m", [])
        wind_values = hourly.get("wind_speed_10m", [])
        soil_values = hourly.get("soil_moisture_0_to_1cm", [])

        current = data.get("current", {})
        current_time = current.get("time")

        if not times or not precipitation or current_time not in times:
            raise RuntimeError("Open-Meteo returned incomplete hourly data.")

        current_index = times.index(current_time)
        start = max(0, current_index - 23)
        recent_24h = [
            float(x or 0.0) for x in precipitation[start: current_index + 1]
        ]

        # Open-Meteo precipitation is the preceding-hour sum.
        rain_1h = recent_24h[-1] if recent_24h else 0.0
        rain_3h = sum(recent_24h[-3:])
        rain_24h = sum(recent_24h)

        humidity = float(
            current.get(
                "relative_humidity_2m",
                humidity_values[current_index] if humidity_values else 75.0,
            )
        )
        temperature = float(
            current.get(
                "temperature_2m",
                temperature_values[current_index] if temperature_values else 22.0,
            )
        )
        wind = float(
            current.get(
                "wind_speed_10m",
                wind_values[current_index] if wind_values else 10.0,
            )
        )

        soil_raw = (
            soil_values[current_index]
            if current_index < len(soil_values)
            else None
        )
        # Volumetric water content is represented as m³/m³ by Open-Meteo.
        # Convert to a simple percentage-like proxy for this prototype.
        if soil_raw is not None:
            soil_moisture = max(0.0, min(float(soil_raw) * 100.0, 100.0))
        else:
            soil_moisture = max(30.0, min(35.0 + rain_24h * 0.45, 95.0))

        return EnvironmentalData(
            rainfall_1h=round(rain_1h, 1),
            rainfall_3h=round(rain_3h, 1),
            rainfall_24h=round(rain_24h, 1),
            rainfall_intensity=round(rain_1h, 1),
            soil_moisture=round(soil_moisture, 1),
            humidity=round(humidity, 1),
            temperature=round(temperature, 1),
            wind_speed=round(wind, 1),
            data_source="LIVE_OPEN_METEO",
        )

    except Exception as exc:
        logger.warning("Live weather API failed: %s. Using explicit demo fallback.", exc)
        return _fallback_data()
