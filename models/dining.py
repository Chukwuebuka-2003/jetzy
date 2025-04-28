from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import time


class RestaurantSearchRequest(BaseModel):
    location: str
    radius_km: Optional[float] = 5.0
    cuisines: Optional[List[str]] = None
    price_range: Optional[List[str]] = None
    open_now: Optional[bool] = None


class RestaurantHours(BaseModel):
    day_of_week: str
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None
    is_closed: bool = False


class RestaurantLocation(BaseModel):
    address: str
    city: str
    region: Optional[str] = None
    country: str
    latitude: float
    longitude: float



class RestaurantOption(BaseModel):
    name: str
    cuisines: List[str]
    price_level: str
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    location: RestaurantLocation
    hours: Optional[List[RestaurantHours]] = None
    phone: Optional[str] = None
    website: Optional[HttpUrl] = None
    reservation_link: Optional[HttpUrl] = None
    image_url: Optional[HttpUrl] = None
    provider: str


class RestaurantSearchResponse(BaseModel):
    options: List[RestaurantOption]
    search_id: str
    search_params: RestaurantSearchRequest

    