from typing import Dict, Any, List, Optional
from models.dining import RestaurantSearchRequest, RestaurantSearchResponse, RestaurantOption, RestaurantLocation, RestaurantHours
from config import settings
from api.mock_data import generate_mock_restaurant

class ZomatoClient:
    """Mock client for Zomato API."""
    
    def __init__(self):
        self.api_key = "mock_key"
    
    async def search_restaurants(self, request: RestaurantSearchRequest) -> RestaurantSearchResponse:
        """Search for restaurants using mock data."""
        # Generate mock restaurant options
        mock_options = generate_mock_restaurant(
            location=request.location,
            cuisines=request.cuisines,
            price_range=request.price_range,
            count=5
        )
        
        # Set the provider to Zomato for all options
        for option in mock_options:
            option["provider"] = "Zomato"
        
        # Convert mock data to RestaurantOption objects
        options = []
        for mock in mock_options:
            hours = []
            for hour_data in mock["hours"]:
                hours.append(
                    RestaurantHours(
                        day_of_week=hour_data["day_of_week"],
                        opening_time=hour_data.get("opening_time"),
                        closing_time=hour_data.get("closing_time"),
                        is_closed=hour_data["is_closed"]
                    )
                )
            
            location = RestaurantLocation(
                address=mock["location"]["address"],
                city=mock["location"]["city"],
                region=mock["location"].get("region"),
                country=mock["location"]["country"],
                latitude=mock["location"]["latitude"],
                longitude=mock["location"]["longitude"]
            )
            
            options.append(
                RestaurantOption(
                    name=mock["name"],
                    cuisines=mock["cuisines"],
                    price_level=mock["price_level"],
                    rating=mock["rating"],
                    reviews_count=mock["reviews_count"],
                    location=location,
                    hours=hours,
                    phone=mock.get("phone"),
                    website=mock.get("website"),
                    reservation_link=mock.get("reservation_link"),
                    image_url=mock.get("image_url"),
                    provider=mock["provider"]
                )
            )
        
        return RestaurantSearchResponse(
            options=options,
            search_id=f"mock-search-zomato-{request.location}",
            search_params=request
        )
    
    async def close(self):
        """Close the HTTP client session."""
        pass  # No real connection to close

