from fastapi import FastAPI, HTTPException, Depends, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import uuid
import json
import asyncio
import logging
import traceback
import os

# Import the models
from models.flights import FlightSearchReqeust, FlightSearchResponse
from models.hotels import HotelSearchRequest, HotelSearchResponse
from models.attractions import AttractionSearchRequest, AttractionSearchResponse
from models.dining import RestaurantSearchRequest, RestaurantSearchResponse
from models.transport import TransportSearchRequest, TransportSearchResponse, TransportMode
from models.user import UserContext
from models.openai import OpenaiRequest, OpenaiResponse

# Import enhanced services
from enhanced_conversation import EnhancedConversationService
from travel_handler import TravelHandler
from link_processor import LinkProcessor

# Check environment variables
if not os.getenv("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY environment variable is not set!")
    print("Chat functionality will not work correctly without this key.")

# Setup logging with more details
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("jetzy_api.log")  # Also log to file
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Jetzy Travel AI API",
    description="API for the Jetzy Travel AI ChatBot",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for user contexts (replace with a database in production)
user_contexts = {}

# Input model for chat requests
class ChatRequest(BaseModel):
    user_id: str
    message: str

# Response model for chat
class ChatLink(BaseModel):
    url: str
    text: str
    type: str = "general"

class ChatResponse(BaseModel):
    response_id: str
    text: str
    links: List[ChatLink] = []
    created_at: datetime

# Initialize services
logger.info("Initializing services...")
try:
    conversation_service = EnhancedConversationService()
    travel_handler = TravelHandler()
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Error initializing services: {str(e)}")
    logger.error(traceback.format_exc())
    raise

# Helper function to get user context
def get_user_context(user_id: str) -> UserContext:
    if user_id not in user_contexts:
        user_contexts[user_id] = UserContext(user_id=user_id)
    return user_contexts[user_id]

# Debug endpoint to test OpenAI API connection
@app.get("/api/debug/openai")
async def debug_openai():
    """Debug endpoint to test OpenAI API connection."""
    from api.chatgpt import ChatGPTClient
    
    logger.info("Debug endpoint called to test OpenAI connection")
    
    client = ChatGPTClient()
    try:
        # Prepare a simple message for testing
        test_message = "Tell me about Jetzy, the travel assistant."
        logger.info(f"Testing with message: {test_message}")
        
        # Send a simple request to OpenAI
        response = await client.generate_response([
            {"role": "system", "content": "You are a helpful assistant called Claude."},
            {"role": "user", "content": test_message}
        ])
        
        # Extract the content
        content = "No content found in response"
        if "choices" in response and len(response["choices"]) > 0 and "message" in response["choices"][0]:
            content = response["choices"][0]["message"]["content"]
            logger.info(f"Received valid response of length {len(content)}")
        else:
            logger.warning(f"Unexpected response format: {response}")
        
        # Return successful result
        return {
            "success": True,
            "test_time": datetime.now(),
            "test_id": str(uuid.uuid4()),
            "response": content,
            "response_metadata": {
                "model": response.get("model", "unknown"),
                "usage": response.get("usage", {}),
                "response_id": response.get("id", "unknown")
            }
        }
    except Exception as e:
        logger.error(f"OpenAI test failed: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return error details
        return {
            "success": False,
            "test_time": datetime.now(),
            "error": str(e),
            "error_type": type(e).__name__,
            "suggestion": "Check your API key, internet connection, and OpenAI service status."
        }
    finally:
        await client.close()

# Chat endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message and return a response."""
    logger.info(f"Processing chat request from user: {request.user_id}")
    logger.info(f"Message: {request.message[:50]}..." if len(request.message) > 50 else f"Message: {request.message}")
    
    try:
        # Get or create user context
        context = get_user_context(request.user_id)
        
        # Process the message with enhanced conversation service
        try:
            logger.info("Calling conversation service")
            response_data = await conversation_service.process_message(
                request.user_id, 
                request.message, 
                context
            )
            logger.info("Conversation service returned successfully")
        except Exception as e:
            logger.error(f"Error in conversation service: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Create a fallback response with error details
            return ChatResponse(
                response_id=str(uuid.uuid4()),
                text=f"I'm having trouble processing your request due to a technical issue. Error: {str(e)}. Please try again in a moment.",
                links=[],
                created_at=datetime.now()
            )
        
        # Update the user context
        user_contexts[request.user_id] = response_data["context"]
        
        # Clean up the response text
        text = LinkProcessor.format_response_with_links(response_data["text"])
        
        # Extract links
        links = response_data.get("links", [])
        chat_links = [ChatLink(**link) for link in links]
        
        logger.info(f"Response generated with {len(chat_links)} links")
        
        # Prepare and return the response
        return ChatResponse(
            response_id=str(uuid.uuid4()),
            text=text,
            links=chat_links,
            created_at=datetime.now()
        )
    except Exception as e:
        logger.error(f"Unhandled error in chat endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return a detailed error response
        return ChatResponse(
            response_id=str(uuid.uuid4()),
            text=f"I'm having technical difficulties. Error: {type(e).__name__}. Please try again later.",
            links=[],
            created_at=datetime.now()
        )

# Flight search endpoint
@app.post("/api/flights/search", response_model=FlightSearchResponse)
async def search_flights(request: FlightSearchReqeust):
    try:
        logger.info(f"Processing flight search: {request.origin} to {request.destination}")
        
        # Process via travel handler
        response = await travel_handler._handle_flight_search({
            "origin": request.origin,
            "destination": request.destination,
            "departure_date": request.departure_date.isoformat(),
            "return_date": request.return_date.isoformat() if request.return_date else None,
            "adults": request.adults,
            "children": request.children,
            "cabin_class": request.cabin_class
        })
        
        return response["data"]
    except Exception as e:
        logger.error(f"Error searching flights: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error searching flights: {str(e)}")

# Restaurant search endpoint
@app.post("/api/restaurants/search", response_model=RestaurantSearchResponse)
async def search_restaurants(request: RestaurantSearchRequest):
    try:
        logger.info(f"Processing restaurant search in {request.location}")
        
        # Process via travel handler
        response = await travel_handler._handle_restaurant_search({
            "location": request.location,
            "cuisines": request.cuisines,
            "price_range": request.price_range,
            "open_now": request.open_now
        })
        
        return response["data"]
    except Exception as e:
        logger.error(f"Error searching restaurants: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error searching restaurants: {str(e)}")

# Transport search endpoint
@app.post("/api/transport/search", response_model=TransportSearchResponse)
async def search_transport(request: TransportSearchRequest):
    try:
        logger.info(f"Processing transport search: {request.origin} to {request.destination}")
        
        # Process via travel handler
        response = await travel_handler._handle_transport_search({
            "origin": request.origin,
            "destination": request.destination,
            "departure_date": request.departure_date.isoformat(),
            "transport_modes": [mode.value for mode in request.modes] if request.modes else None,
            "adults": request.adults,
            "children": request.children
        })
        
        return response["data"]
    except Exception as e:
        logger.error(f"Error searching transport: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error searching transport: {str(e)}")

# Get user preferences endpoint
@app.get("/api/user/{user_id}/preferences")
async def get_user_preferences(user_id: str):
    try:
        context = get_user_context(user_id)
        return {
            "user_id": user_id,
            "preferences": context.preferences
        }
    except Exception as e:
        logger.error(f"Error retrieving user preferences: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error retrieving user preferences: {str(e)}")

# Update user preferences endpoint
@app.put("/api/user/{user_id}/preferences")
async def update_user_preferences(user_id: str, preferences: Dict[str, Any]):
    try:
        context = get_user_context(user_id)
        
        if context.preferences:
            # Update existing preferences
            for key, value in preferences.items():
                setattr(context.preferences, key, value)
        else:
            # Create new preferences object
            from models.user import UserPreference
            context.preferences = UserPreference(**preferences)
        
        # Update context in storage
        user_contexts[user_id] = context
        
        return {
            "user_id": user_id,
            "preferences": context.preferences,
            "message": "Preferences updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating user preferences: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error updating user preferences: {str(e)}")

# Update user location endpoint
@app.put("/api/user/{user_id}/location")
async def update_user_location(user_id: str, location: Dict[str, Any]):
    try:
        context = get_user_context(user_id)
        
        # Create or update location
        from models.user import UserLocation
        context.location = UserLocation(
            **location,
            last_updated=datetime.now()
        )
        
        # Update context in storage
        user_contexts[user_id] = context
        
        return {
            "user_id": user_id,
            "location": context.location,
            "message": "Location updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating user location: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error updating user location: {str(e)}")

# Error handler middleware
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled exception in middleware: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return a detailed error response
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred.",
                "error_type": type(e).__name__,
                "error": str(e)
            }
        )

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "online",
        "version": "1.0.0",
        "timestamp": datetime.now(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Shutdown event to close clients
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down API services")
    
    # Close conversation service
    try:
        await conversation_service.close()
        logger.info("Conversation service closed")
    except Exception as e:
        logger.error(f"Error closing conversation service: {str(e)}")
    
    logger.info("All services closed successfully")

if __name__ == "__main__":
    import uvicorn
    
    # Log startup information
    logger.info("Starting Jetzy Travel AI API server")
    logger.info(f"OpenAI API Key configured: {bool(os.getenv('OPENAI_API_KEY'))}")
    
    # Run the server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)