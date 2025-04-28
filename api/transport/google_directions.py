from typing import Dict, Any, List, Optional
from datetime import datetime
from models.transport import TransportSearchRequest, TransportSearchResponse, TransportOption, TransportSegment, TransportMode
from config import settings
from api.mock_data import generate_mock_transport

class GoogleDirectionsClient:
    """Mock client for Google Directions API."""
    
    def __init__(self):
        self.api_key = "mock_key"
    
    async def search_transport(self, request: TransportSearchRequest) -> TransportSearchResponse:
        """Search for transport options using mock data."""
        # Generate mock transport options
        mock_options = generate_mock_transport(
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            count=4
        )
        
        # Set the provider to Google Directions for all options
        for option in mock_options:
            option["provider"] = "Google Directions"
        
        # Filter by transport modes if specified
        if request.modes:
            mock_options = [
                option for option in mock_options 
                if any(segment["mode"] in [mode.value for mode in request.modes] for segment in option["segments"])
            ]
        
        # Convert mock data to TransportOption objects
        options = []
        for mock in mock_options:
            segments = []
            for segment_data in mock["segments"]:
                segments.append(
                    TransportSegment(
                        mode=TransportMode(segment_data["mode"]),
                        provider=segment_data.get("provider"),
                        departure_location=segment_data["departure_location"],
                        departure_time=segment_data["departure_time"],
                        arrival_location=segment_data["arrival_location"],
                        arrival_time=segment_data["arrival_time"],
                        duration_minutes=segment_data["duration_minutes"],
                        distance_km=segment_data.get("distance_km")
                    )
                )
            
            options.append(
                TransportOption(
                    segments=segments,
                    total_duration_minutes=mock["total_duration_minutes"],
                    total_price=mock["total_price"],
                    currency=mock["currency"],
                    booking_link=mock["booking_link"],
                    provider=mock["provider"]
                )
            )
        
        return TransportSearchResponse(
            options=options,
            search_id=f"mock-search-google-directions-{request.origin}-{request.destination}",
            search_params=request,
            currency="USD"
        )
    
    async def close(self):
        """Close the HTTP client session."""
        pass  # No real connection to close
