import logging
from datetime import datetime, timezone

from ..database.mongodb import db_manager
from ..ml.predict import predict_landslide_probability
from ..models.schemas import EnvironmentalData, RiskResult
from ..services.terrain_service import get_terrain_info
from ..services.weather_service import fetch_environmental_data

logger = logging.getLogger(__name__)


def classify_risk(probability: float) -> tuple[int, str]:
    score = int(round(max(0.0, min(probability, 1.0)) * 100))
    if score >= 81:
        return score, "CRITICAL"
    if score >= 61:
        return score, "HIGH"
    if score >= 31:
        return score, "MODERATE"
    return score, "LOW"


async def calculate_risk_assessment(
    location_name: str, lat: float, lon: float
) -> RiskResult:
    if not location_name.strip():
        location_name = f"Lat {lat:.4f}, Lon {lon:.4f}"

    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Invalid latitude/longitude.")

    env: EnvironmentalData = await fetch_environmental_data(lat, lon)

    slope, elevation, hist_freq = get_terrain_info(location_name, lat, lon)
    env.slope = slope
    env.elevation = elevation

    features = {
        "rainfall_24h": env.rainfall_24h,
        "rainfall_intensity": env.rainfall_intensity,
        "soil_moisture": env.soil_moisture,
        "humidity": env.humidity,
        "temperature": env.temperature,
        "slope": env.slope,
        "elevation": env.elevation,
        "historical_freq": hist_freq,
    }

    probability = predict_landslide_probability(features)
    score, level = classify_risk(probability)

    factors = {
        "rainfall": "HIGH" if env.rainfall_24h > 50 else "NORMAL",
        "soil_moisture": "HIGH" if env.soil_moisture > 75 else "NORMAL",
        "slope": "HIGH" if env.slope > 32 else "MODERATE",
        "historical_risk": "HIGH" if hist_freq >= 6 else "MODERATE",
    }

    if level in ("CRITICAL", "HIGH"):
        recommendation = (
            "Immediate monitoring and early-warning response action recommended. "
            "Stay away from vulnerable slopes and follow local advisories."
        )
    elif level == "MODERATE":
        recommendation = (
            "Heightened monitoring advised. Track rainfall and local weather advisories."
        )
    else:
        recommendation = "Normal conditions. Continue standard geological observation."

    timestamp = datetime.now(timezone.utc).isoformat()

    result = RiskResult(
        location=location_name,
        latitude=lat,
        longitude=lon,
        risk_score=score,
        risk_level=level,
        risk_probability=round(probability, 4),
        factors=factors,
        recommendation=recommendation,
        timestamp=timestamp,
        environmental_data=env,
    )

    # Database failure must be visible. Never silently pretend a save worked.
    try:
        db_manager.risk_assessments.insert_one(result.model_dump())

        if score >= 61:
            db_manager.alerts.insert_one(
                {
                    "location": location_name,
                    "latitude": lat,
                    "longitude": lon,
                    "risk_score": score,
                    "risk_level": level,
                    "reasons": [
                        f"{key.replace('_', ' ')} is {value}"
                        for key, value in factors.items()
                        if value == "HIGH"
                    ],
                    "recommendation": recommendation,
                    "timestamp": timestamp,
                }
            )

    except Exception as exc:
        logger.exception("Failed to persist risk assessment to MongoDB.")
        raise RuntimeError(
            "Risk calculation succeeded, but MongoDB persistence failed."
        ) from exc

    return result
