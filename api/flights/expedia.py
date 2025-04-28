from typing import Dict, Any, Optional
from models.flights import FlightSearchReqeust, FlightSearchResponse, FlightOption, FlightSegment
from config import settings
from api.mock_data import generate_mock_flight

class ExpediaClient: 
    def __init__(self):
        self.api_key = "mock_key"

    async def search_flights(self, request: FlightSearchReqeust) -> FlightSearchResponse:
        mock_options = generate_mock_flight(
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            return_date=request.return_date,
            count=5
        )

        # Set the provider to Expedia for all options
        for option in mock_options:
            option["provider"] = "Expedia"
        
        options = []
        for mock in mock_options:
            outbound_segments = []
            for segment in mock["outbound_segments"]:
                outbound_segments.append(
                    FlightSegment(
                        airline=segment["airline"],
                        flight_number=segment["flight_number"],
                        departure_airport=segment["departure_airport"],
                        departure_time=segment["departure_time"],
                        arrival_airport=segment["arrival_airport"],
                        arrival_time=segment["arrival_time"],
                        duration_minutes=segment["duration_minutes"],
                        cabin_class=segment["cabin_class"]
                    )
                )

            return_segments = None

            if mock["return_segments"]:
                return_segments = []
                for segment in mock["return_segments"]:
                    return_segments.append(
                        FlightSegment(
                            airline=segment["airline"],
                            flight_number=segment["flight_number"],
                            departure_airport=segment["departure_airport"],
                            departure_time=segment["departure_time"],
                            arrival_airport=segment["arrival_airport"],
                            arrival_time=segment["arrival_time"],
                            duration_minutes=segment["duration_minutes"],
                            cabin_class=segment["cabin_class"]
                        )
                    )

            options.append(
                FlightOption(
                    outbound_segments=outbound_segments,
                    return_segments=return_segments,
                    total_price=mock["total_price"],
                    currency=mock["currency"],
                    booking_link=mock["booking_link"],
                    provider=mock["provider"]
                )
            )
            
        return FlightSearchResponse(
            options=options,
            search_id=f"mock-search-expedia-{request.origin}-{request.destination}",
            currency="USD",
            search_params=request
        )
    
    async def close(self):
        """Close the HTTP client session."""
        pass  # No real connection to close in the mock implementation