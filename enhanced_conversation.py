from typing import Dict, Any, List, Optional
import json
import traceback
from datetime import datetime
import logging

from models.user import UserContext
from api.chatgpt import ChatGPTClient
from utils.context import extract_entities
from travel_handler import TravelHandler
from link_processor import LinkProcessor

# Setup detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class EnhancedConversationService:
    """Enhanced service for handling travel conversations with integrated API data."""
    
    def __init__(self):
        logger.info("Initializing EnhancedConversationService")
        self.chatgpt_client = ChatGPTClient()
        self.travel_handler = TravelHandler()
        logger.info("EnhancedConversationService initialized successfully")
    
    async def process_message(self, user_id: str, message: str, context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Process a user message, extract entities, fetch relevant data, and generate a response."""
        logger.info(f"Processing message for user {user_id}: {message[:30]}...")
        
        # Initialize or update user context
        if not context:
            logger.info(f"Creating new context for user {user_id}")
            context = UserContext(user_id=user_id)
        
        
        context.conversation_history.append({"role": "user", "content": message})
        context.last_interaction = datetime.now()
        
        try:
            # Extract entities from the message
            logger.info("Extracting entities from message")
            entities = await extract_entities(message, context)
            logger.info(f"Extracted entities: {entities}")
            
            # Get intent from entities
            intent = entities.get("intent", "general")
            logger.info(f"Detected intent: {intent}")
            
            # Process the intent and get relevant data
            logger.info(f"Processing travel intent: {intent}")
            handler_response = await self.travel_handler.process_travel_intent(intent, entities, context)
            logger.debug(f"Handler response: {json.dumps(handler_response, default=str)[:200]}...")
            
            # Generate response using ChatGPT with the fetched data
            logger.info("Generating response with ChatGPT")
            response_data = await self._generate_response(message, entities, handler_response, context)
            
            # Update conversation history with assistant response
            context.conversation_history.append({"role": "assistant", "content": response_data["text"]})
            
            # Extract links from the response (if any)
            links = handler_response.get("links", [])
            if not links:
                links = LinkProcessor.extract_links(response_data["text"])
            logger.info(f"Found {len(links)} links for the response")
            
            return {
                "text": response_data["text"],
                "links": links,
                "context": context
            }
        except Exception as e:
            # Log the full exception with stack trace
            logger.error(f"Error processing message: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            
            
            error_type = type(e).__name__
            return {
                "text": f"I'm having trouble processing your request. There was an error: {error_type}. Please try again in a moment, or let me know if I can help with something else.",
                "links": [],
                "context": context
            }
    
    async def _generate_response(self, message: str, entities: Dict[str, Any], 
                                handler_response: Dict[str, Any], context: UserContext) -> Dict[str, Any]:
        """Generate a response using ChatGPT with the extracted entities and fetched data."""
        logger.info("Generating response with ChatGPT")
        
        # Create a system prompt
        system_prompt = {
            "role": "system", 
            "content": (
                "You are Jetzy, a knowledgeable and helpful travel assistant. "
                "Provide accurate, concise travel information with a friendly tone. "
                "When responding to travel queries:"
                "\n1. Be direct and specific - prioritize giving concrete information first"
                "\n2. Include exact details when available (prices, times, locations, ratings)"
                "\n3. Use a concise, informative style without unnecessary fillers"
                "\n4. For attractions and places to visit, list the most notable options"
                "\n5. End your response with '<Links to these places>' or similar link placeholder text"
                "\n6. Don't use phrases like 'I recommend' or 'I suggest' - just state the facts"
                "\n7. Avoid questions to the user unless specifically needed for clarification"
                "\n8. Format responses like these examples:"
                
                "\n\nExample 1:"
                "\nQuestion: Find me a flight to Greece."
                "\nAnswer: Flights from New York to Greece usually fly from the JFK airport. Usually return flights cost around $600, on Airlines such as United, American, Lufthansa and Air France. Norwegian has the cheapest deals at $400. There's a flight on Norwegian leaving New York 18th April to Athens, and back on 30th April for $403. <Links to book flights>"
                
                "\n\nExample 2:"
                "\nQuestion: What are the best places to visit in New York City?"
                "\nAnswer: New York City is packed with iconic landmarks and tourist attractions. Tourists love visiting Times Square, Central Park and Statue of Liberty. Museum lovers appreciate the Metropolitan Museum of Art, and American Museum of Natural History. Greenwich Village and Soho are interesting neighborhoods to explore, while catching a Broadway show is a must for entertainment lovers. New York has something for everyone. <Links to these places>"
                
                "\n\nExample 3:"
                "\nQuestion: What are the best rated restaurants near me?"
                "\nAnswer: Your location shows you are in New York City. The best rated restaurants here are Le Bernardin (French), Per Se (new American), Daniel (French), and Jungsik (Korean). <Links to make reservations at these restaurants>"
            )
        }
        
        
        content_message = {
            "role": "system",
            "content": f"Here's the data retrieved for the user's query:\n{json.dumps(handler_response, default=str)}\n\n"
                      f"Please use this data to provide a helpful response to the user's query: '{message}'"
        }
        
        # Get conversation history (last 5 exchanges)
        history_limit = 10  
        start_idx = max(0, len(context.conversation_history) - history_limit)
        history = context.conversation_history[start_idx:]
        
        
        logger.debug(f"System prompt: {system_prompt['content'][:100]}...")
        logger.debug(f"Content message: {content_message['content'][:100]}...")
        logger.debug(f"Including {len(history)} conversation history messages")
        
        
        messages = [system_prompt, content_message] + history
        
        try:
            # Get response from ChatGPT
            logger.info("Calling ChatGPT API")
            response = await self.chatgpt_client.generate_response(
                messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            logger.info("Successfully received response from ChatGPT API")
            
            # Extract the content from the response
            if "choices" in response and len(response["choices"]) > 0 and "message" in response["choices"][0]:
                content = response["choices"][0]["message"]["content"]
                logger.info(f"Extracted content: {content[:100]}...")
                
                
                intent = entities.get("intent", "")
                if intent == "attraction" and "<Links to these places>" not in content and "<Links to " not in content:
                    content += " <Links to these places>"
                    logger.info("Added missing link placeholder for attraction response")
                
                return {
                    "text": content
                }
            else:
                logger.error(f"Unexpected response format: {response}")
                raise ValueError("Unexpected response format from OpenAI API")
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            
            # Re-raise the exception to be caught by the main process_message method
            raise
    
    def _extract_links(self, text: str) -> List[Dict[str, str]]:
        """Extract links from response text."""
        return LinkProcessor.extract_links(text)
    
    async def close(self):
        """Close all client connections."""
        try:
            logger.info("Closing client connections")
            await self.chatgpt_client.close()
            await self.travel_handler.close()
            logger.info("All client connections closed")
        except Exception as e:
            logger.error(f"Error closing connections: {str(e)}")