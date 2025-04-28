from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from enum import Enum, auto


class TransportMode(str, Enum):
    TRAIN = "train"
    BUS = "bus" 
    FLIGHT = "flight"
    CAR = "car"
    FERRY = "ferry"
    SUBWAY = "subway"
    WALK = "walk"

class TransportSearchRequest(BaseModel):
    origin: str
    destination: str
    departure_date: datetime
    modes: Optional[List[TransportMode]] = None
    adults: int = Field(default=1, ge=1)
    children: int = Field(default=0, ge=0)

class TransportSegment(BaseModel):
    mode: TransportMode
    provider: Optional[str] = None
    departure_location: str
    departure_time: datetime
    arrival_location: str
    arrival_time: datetime
    duration_minutes: int
    distance_km: Optional[float] = None

class TransportOption(BaseModel):
    segments: List[TransportSegment]
    total_duration_minutes: int
    total_price: float
    currency: str = "USD"
    booking_link: Optional[HttpUrl] = None
    provider: str

class TransportSearchResponse(BaseModel):
    options: List[TransportOption]
    search_id: str
    currency: str = "USD"
    search_params: TransportSearchRequest