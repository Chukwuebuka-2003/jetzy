from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class UserPreference(BaseModel):
    preferrred_airlines: Optional[List[str]] = None
    preferred_hotel_chains: Optional[List[str]] = None
    budget_range_usd: Optional[tuple[float, float]] = None
    preferred_cuisines: Optional[List[str]] = None
    travel_style: Optional[str] = None
    accessibility_needs: Optional[List[str]] = None


class UserLocation(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    last_updated: Optional[datetime] = None


class UserContext(BaseModel):
    user_id: str
    location: Optional[UserLocation] = None
    preferences: Optional[UserPreference] = None
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    last_interaction: Optional[datetime] = None