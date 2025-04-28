from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import date, datetime

class FlightSearchReqeust(BaseModel):
    origin: str
    destination: str
    departure_date: date
    return_date: Optional[date] = None
    adults: int = Field(default=1, ge=1)
    children: int = Field(default=0, ge=0)
    infants: int = Field(default=0, ge=0)
    cabin_class: str = Field(default="economy")
    direct_flights_only: bool = Field(default=False)


class FlightSegment(BaseModel):
    airline: str
    flight_number: str
    departure_airport: str
    departure_time: datetime
    arrival_airport: str
    arrival_time: datetime
    duration_minutes: int
    cabin_class: str


class FlightOption(BaseModel):
    outbound_segments: List[FlightSegment]
    return_segments: Optional[List[FlightSegment]] = None
    total_price: float
    currency: str = "USD"
    booking_link:  HttpUrl
    provider: str


class FlightSearchResponse(BaseModel):
    options: List[FlightOption]
    search_id: str
    currency: str = "USD"
    search_params: FlightSearchReqeust