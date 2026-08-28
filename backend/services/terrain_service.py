import httpx
from typing import Tuple

# Predefined geological slope and elevation lookup for North-Eastern Region
NER_TERRAIN_MAP = {
    "gangtok": (36.0, 1650.0, 8),
    "shillong": (28.0, 1525.0, 5),
    "aizawl": (42.0, 1132.0, 9),
    "kohima": (34.0, 1444.0, 6),
    "itanagar": (30.0, 320.0, 4),
    "guwahati": (12.0, 55.0, 2),
    "imphal": (22.0, 786.0, 3),
    "agartala": (8.0, 15.0, 1)
}

def get_terrain_info(location_name: str, lat: float, lon: float) -> Tuple[float, float, int]:
    """
    Returns (slope_degrees, elevation_meters, historical_frequency).
    Uses NER documented geological records with fallback.
    """
    norm_name = location_name.lower()
    for key, val in NER_TERRAIN_MAP.items():
        if key in norm_name:
            return val
    
    # Default approximation for mountainous NER terrain
    return (25.0, 1100.0, 4)