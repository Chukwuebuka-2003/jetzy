from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date, timedelta
import asyncio
import logging
from pydantic import BaseModel

# Import models
from models.flights import FlightSearchReqeust, FlightSearchResponse
from models.hotels import HotelSearchRequest, HotelSearchResponse
from models.attractions import AttractionSearchRequest, AttractionSearchResponse
from models.dining import RestaurantSearchRequest, RestaurantSearchResponse
from models.transport import TransportSearchRequest, TransportSearchResponse, TransportMode
from models.user import UserContext

# Import API clients - fixed paths to match your directory structure
from api.flights.skyscanner import SkyscannerClient
from api.flights.expedia import ExpediaClient
from api.dining.yelp import YelpClient
from api.dining.zomato import ZomatoClient
from api.transport.rome2rio import Rome2RioClient
from api.transport.google_directions import GoogleDirectionsClient
from api.chatgpt import ChatGPTClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TravelHandler:
    """Handler for processing travel-related queries and fetching appropriate data."""
    
    def __init__(self):
        # Initialize API clients
        self.flight_clients = {
            "skyscanner": SkyscannerClient(),
            "expedia": ExpediaClient()
        }
        
        self.restaurant_clients = {
            "yelp": YelpClient(),
            "zomato": ZomatoClient()
        }
        
        self.transport_clients = {
            "rome2rio": Rome2RioClient(),
            "google": GoogleDirectionsClient()
        }
        
        self.chatgpt_client = ChatGPTClient()
    
    async def process_travel_intent(self, intent: str, entities: Dict[str, Any], context: UserContext) -> Dict[str, Any]:
        """Process the extracted travel intent and fetch relevant data."""
        logger.info(f"Processing intent: {intent}")
        
        try:
            # Process based on intent type
            if intent == "flight":
                return await self._handle_flight_search(entities)
            elif intent == "hotel":
                return await self._handle_hotel_search(entities)
            elif intent == "restaurant":
                return await self._handle_restaurant_search(entities)
            elif intent == "attraction":
                return await self._handle_attraction_search(entities)
            elif intent == "transport":
                return await self._handle_transport_search(entities)
            elif intent == "seasonal_advice":
                return await self._handle_seasonal_advice(entities)
            else:
                # For general intent, no specific data fetching needed
                return {"type": "general", "data": None}
        except Exception as e:
            logger.error(f"Error processing travel intent: {str(e)}")
            return {"type": "error", "message": str(e)}
    
    async def _handle_flight_search(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle flight search queries."""
        # Extract required parameters
        origin = entities.get("origin")
        destination = entities.get("destination")
        
        if not origin or not destination:
            return {"type": "flight", "data": None, "message": "Missing origin or destination for flight search"}
        
        # Parse dates
        departure_date = self._parse_date(entities.get("departure_date"))
        return_date = self._parse_date(entities.get("return_date"))
        
        if not departure_date:
            # Default to tomorrow if not specified
            departure_date = date.today() + timedelta(days=1)
        
        # Prepare search request
        request = FlightSearchReqeust(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=entities.get("adults", 1),
            children=entities.get("children", 0),
            infants=entities.get("infants", 0),
            cabin_class=entities.get("cabin_class", "economy"),
            direct_flights_only=entities.get("direct_flights_only", False)
        )
        
        # Perform search
        client = self.flight_clients["skyscanner"]  # Use Skyscanner by default
        response = await client.search_flights(request)
        
        return {
            "type": "flight",
            "data": response,
            "message": "Flight options retrieved successfully"
        }
    
    async def _handle_restaurant_search(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle restaurant search queries."""
        # Extract location
        location = entities.get("location")
        
        if not location:
            return {"type": "restaurant", "data": None, "message": "Missing location for restaurant search"}
        
        # Prepare search request
        request = RestaurantSearchRequest(
            location=location,
            radius_km=entities.get("radius_km", 5.0),
            cuisines=entities.get("cuisines"),
            price_range=entities.get("price_range"),
            open_now=entities.get("open_now")
        )
        
        # Perform search
        client = self.restaurant_clients["yelp"]  # Use Yelp by default
        response = await client.search_restaurants(request)
        
        return {
            "type": "restaurant",
            "data": response,
            "message": "Restaurant options retrieved successfully"
        }
    
    async def _handle_transport_search(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle transport search queries."""
        # Extract required parameters
        origin = entities.get("origin")
        destination = entities.get("destination")
        
        if not origin or not destination:
            return {"type": "transport", "data": None, "message": "Missing origin or destination for transport search"}
        
        # Parse date
        departure_date = self._parse_datetime(entities.get("departure_date"))
        
        if not departure_date:
            # Default to tomorrow at noon if not specified
            tomorrow = date.today() + timedelta(days=1)
            departure_date = datetime.combine(tomorrow, datetime.min.time().replace(hour=12))
        
        # Parse transport modes
        modes = None
        if "transport_modes" in entities:
            modes = []
            for mode in entities["transport_modes"]:
                if hasattr(TransportMode, mode.upper()):
                    modes.append(getattr(TransportMode, mode.upper()))
        
        # Prepare search request
        request = TransportSearchRequest(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            modes=modes,
            adults=entities.get("adults", 1),
            children=entities.get("children", 0)
        )
        
        # Perform search
        client = self.transport_clients["rome2rio"]  # Use Rome2Rio by default
        response = await client.search_transport(request)
        
        return {
            "type": "transport",
            "data": response,
            "message": "Transport options retrieved successfully"
        }
    
    async def _handle_hotel_search(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle hotel search queries."""
        # For now, just return a placeholder since our hotel clients aren't fully implemented
        return {
            "type": "hotel",
            "data": None,
            "message": "Hotel search functionality coming soon"
        }
    
    async def _handle_attraction_search(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle attraction search queries."""
        # For now, just return a placeholder since our attraction clients aren't fully implemented
        return {
            "type": "attraction",
            "data": None,
            "message": "Attraction search functionality coming soon"
        }
    
    async def _handle_seasonal_advice(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle seasonal travel advice queries."""
        # For seasonal advice, we would typically use ChatGPT directly
        return {
            "type": "seasonal_advice",
            "data": None,
            "message": "Seasonal advice functionality coming soon"
        }
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date string into a date object."""
        if not date_str:
            return None
        
        try:
            return date.fromisoformat(date_str)
        except (ValueError, TypeError):
            logger.warning(f"Invalid date format: {date_str}")
            return None
    
    def _parse_datetime(self, datetime_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string into a datetime object."""
        if not datetime_str:
            return None
        
        try:
            return datetime.fromisoformat(datetime_str)
        except (ValueError, TypeError):
            # Try parsing as date if datetime fails
            try:
                parsed_date = self._parse_date(datetime_str)
                if parsed_date:
                    return datetime.combine(parsed_date, datetime.min.time().replace(hour=12))
                return None
            except:
                logger.warning(f"Invalid datetime format: {datetime_str}")
                return None
    
    async def close(self):
        """Close all API clients."""
        close_tasks = []
        
        # Close flight clients
        for client in self.flight_clients.values():
            close_tasks.append(client.close())
        
        # Close restaurant clients
        for client in self.restaurant_clients.values():
            close_tasks.append(client.close())
        
        # Close transport clients
        for client in self.transport_clients.values():
            close_tasks.append(client.close())
        
        # Close ChatGPT client
        close_tasks.append(self.chatgpt_client.close())
        
        # Wait for all clients to close
        await asyncio.gather(*close_tasks)