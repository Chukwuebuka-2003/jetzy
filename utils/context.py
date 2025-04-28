# utils/context.py
from typing import Dict, Any, List, Optional
import json
import logging
from models.user import UserContext
from api.chatgpt import ChatGPTClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def extract_entities(message: str, context: UserContext) -> Dict[str, Any]:
    """
    Extract relevant travel-related entities from user message using ChatGPT.
    
    This function utilizes the ChatGPT API to identify and extract structured 
    travel information from natural language queries.
    
    Returns a dictionary of extracted entities.
    """
    # Create a ChatGPT client
    logger.info("Extracting entities from message")
    chatgpt_client = ChatGPTClient()
    
    # Craft a detailed system prompt to guide entity extraction
    system_prompt = {
        "role": "system",
        "content": """
        You are an expert travel entity extraction system. Your task is to analyze user travel queries 
        and extract structured information. Identify and extract the following travel-related entities 
        when they are explicitly or implicitly mentioned:
        
        - intent: The primary travel intent (flight, hotel, attraction, restaurant, transport, seasonal_advice, general)
        - origin: Origin location for travel (city, airport code)
        - destination: Destination location for travel (city, country, region)
        - departure_date: Departure date in YYYY-MM-DD format (convert relative dates like "next Friday")
        - return_date: Return date in YYYY-MM-DD format (for round trips)
        - check_in_date: Check-in date for accommodation in YYYY-MM-DD format
        - check_out_date: Check-out date for accommodation in YYYY-MM-DD format
        - adults: Number of adults traveling (default to 1 if traveling is mentioned but no number specified)
        - children: Number of children traveling
        - location: Location for attractions/restaurants (if asking about places to visit, use this field)
        - cuisines: Types of cuisine (for restaurant queries)
        - categories: Types of attractions (museum, historical, park, etc.)
        - price_range: Budget constraints (can be "$", "$$", "$$$", "$$$$" or min-max values)
        - min_price: Minimum price if specified
        - max_price: Maximum price if specified
        - transport_modes: Preferred modes of transportation (train, flight, bus, car, etc.)
        - travel_season: Season or time period mentioned for travel
        
        Return a JSON object with these fields. If a field is not present in the query, omit it.
        Be precise in extracting exact values and don't include fields that aren't specifically mentioned.
        Use standard formats for dates (YYYY-MM-DD) and normalize location names (e.g., "NYC" → "New York").
        
        Important: If the query is about places to visit, attractions, or things to do in a location, 
        set the intent to "attraction" and extract the location. For example, with "What are the best 
        places to visit in New York City?", set intent to "attraction" and location to "New York City".
        
        For example, for "I need a flight from NYC to Paris next Friday returning Tuesday", extract:
        {
          "intent": "flight",
          "origin": "New York",
          "destination": "Paris",
          "departure_date": "YYYY-MM-DD", // calculated date for next Friday
          "return_date": "YYYY-MM-DD", // calculated date for next Tuesday
          "adults": 1
        }
        """
    }
    
    # Include the current message and some context from previous messages
    conversation_history = []
    if context.conversation_history:
        # Get the last few exchanges for context
        start_idx = max(0, len(context.conversation_history) - 4)
        conversation_history = context.conversation_history[start_idx:]
    
    messages = [system_prompt] + conversation_history + [{"role": "user", "content": message}]
    
    # Get entity extraction from ChatGPT
    try:
        logger.info("Sending entity extraction request to ChatGPT")
        response = await chatgpt_client.generate_response(
            messages,
            temperature=0.2,  # Lower temperature for more deterministic output
            max_tokens=500
        )
        
        # Process the response to extract the JSON object
        content = response["choices"][0]["message"]["content"]
        logger.info(f"Received entity extraction response: {content[:100]}...")
        
        # Extract JSON from the response
        try:
            # Look for JSON in the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                entities = json.loads(json_str)
                logger.info(f"Extracted entities: {entities}")
            else:
                # If no JSON found, create a basic object with intent
                logger.warning("No JSON structure found in response")
                entities = {"intent": "general"}
        except json.JSONDecodeError:
            # If JSON parsing fails, create a basic object
            logger.error("Failed to parse JSON from response")
            entities = {"intent": "general"}
    except Exception as e:
        # Handle any API errors
        logger.error(f"Error extracting entities: {str(e)}")
        entities = {"intent": "general"}
    
    # Clean up
    await chatgpt_client.close()
    
    return entities