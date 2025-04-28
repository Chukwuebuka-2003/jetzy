from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import time

class AttractionSearchRequest(BaseModel):
    location: str
    radius_km: Optional[float] = 5.0
    categories: Optional[List[str]] = None
    family_friendly: Optional[bool] = None


class AttractionHours(BaseModel):
    day_of_week: str
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None
    is_closed: bool = False


class AttractionLocation(BaseModel):
    address: str
    city: str
    region: Optional[str] = None
    country: str
    latitude: float
    longitude: float

class AttractionOption(BaseModel):
    name: str
    description: str
    category: List[str]
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    price_range: Optional[str] = None
    estimated_duration: Optional[int] = None
    location: AttractionLocation
    hours: Optional[List[AttractionHours]] = None
    website: Optional[HttpUrl] = None
    booking_link: Optional[HttpUrl] = None
    image_url: Optional[HttpUrl] = None
    provider: str


class AttractionSearchResponse(BaseModel):
    options: List[AttractionOption]
    search_id: str
    search_params: AttractionSearchRequest

    