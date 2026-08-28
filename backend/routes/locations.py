from fastapi import APIRouter
from typing import List

router = APIRouter()

PREDEFINED_LOCATIONS = [
    {"name": "Gangtok, Sikkim", "state": "Sikkim", "latitude": 27.3389, "longitude": 88.6065},
    {"name": "Shillong, Meghalaya", "state": "Meghalaya", "latitude": 25.5788, "longitude": 91.8933},
    {"name": "Aizawl, Mizoram", "state": "Mizoram", "latitude": 23.7271, "longitude": 92.7176},
    {"name": "Kohima, Nagaland", "state": "Nagaland", "latitude": 25.6740, "longitude": 94.1086},
    {"name": "Itanagar, Arunachal Pradesh", "state": "Arunachal Pradesh", "latitude": 27.0844, "longitude": 93.6053},
    {"name": "Guwahati, Assam", "state": "Assam", "latitude": 26.1445, "longitude": 91.7362},
    {"name": "Imphal, Manipur", "state": "Manipur", "latitude": 24.8170, "longitude": 93.9368},
    {"name": "Agartala, Tripura", "state": "Tripura", "latitude": 23.8315, "longitude": 91.2868}
]

@router.get("/location/search")
async def search_locations(q: str = ""):
    if not q:
        return PREDEFINED_LOCATIONS
    query = q.lower()
    return [loc for loc in PREDEFINED_LOCATIONS if query in loc["name"].lower() or query in loc["state"].lower()]