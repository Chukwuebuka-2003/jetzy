from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import date

class HotelSearchRequest(BaseModel):
    destination: str
    check_in_date: date
    chedck_out_date: date
    adults: int = Field(default=2, ge=1)
    children: int = Field(default=0, ge=0)
    rooms: int = Field(default=1, ge=1)
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    star_rating: Optional[List[int]] = None
    amenities: Optional[List[str]] = None

class HotelAmenity(BaseModel):
    name: str
    category: str

class HotelLocation(BaseModel):
    address: str
    city: str
    region: Optional[str] = None
    country: str
    postal_code: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class HotelOption(BaseModel):
    name: str
    star_rating: float
    user_rating: Optional[float] = None
    reviews_count: Optional[float] = None
    location: HotelLocation
    price_per_night: float
    total_price: float
    currency: str = "USD"
    amenities: List[HotelAmenity]
    booking_link: HttpUrl
    provider: str
    image_url: Optional[HttpUrl] = None


class HotelSearchResponse(BaseModel):
    options: List[HotelOption]
    search_id: str
    currency: str = "USD"
    search_params: HotelSearchRequest