from typing import Dict, Optional

from pydantic import BaseModel, Field


class LocationItem(BaseModel):
    name: str
    state: str
    latitude: float
    longitude: float
    slope: float
    elevation: float
    historical_frequency: int


class PredictRequest(BaseModel):
    location_name: str = Field(min_length=1, max_length=200)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class EnvironmentalData(BaseModel):
    rainfall_1h: float = 0.0
    rainfall_3h: float = 0.0
    rainfall_24h: float = 0.0
    rainfall_intensity: float = 0.0
    soil_moisture: float = 50.0
    humidity: float = 75.0
    temperature: float = 22.0
    wind_speed: float = 10.0
    slope: float = 25.0
    elevation: float = 1000.0
    data_source: str = "LIVE_API"


class RiskResult(BaseModel):
    location: str
    latitude: float
    longitude: float
    risk_score: int
    risk_level: str
    risk_probability: float
    factors: Dict[str, str]
    recommendation: str
    timestamp: str
    environmental_data: EnvironmentalData


class CitizenRegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=7, max_length=20)
    location: str = Field(min_length=1, max_length=200)


class SOSBroadcastRequest(BaseModel):
    location: str = Field(min_length=1, max_length=200)
    custom_message: Optional[str] = Field(default=None, max_length=500)
