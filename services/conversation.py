# services/conversation.py
from typing import Dict, Any, Optional
import json
from datetime import datetime
from models.user import UserContext
from api.chatgpt import ChatGPTClient

class ConversationService:
    """Service for handling conversations with users using ChatGPT."""
    
    def __init__(self):
        self.chatgpt_client = ChatGPTClient()
    
    async def process_message(self, user_id: str, message: str, context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Process a user message and generate a response using ChatGPT."""
        # Initialize or update user context
        if not context:
            context = UserContext(user_id=user_id)
        
        # Update conversation history
        context.conversation_history.append({"role": "user", "content": message})
        context.last_interaction = datetime.now()
        
        # Process the message with ChatGPT
        response_data = await self._handle_query(message, context)
        
        # Update conversation history with assistant response
        context.conversation_history.append({"role": "assistant", "content": response_data["text"]})
        
        return {
            "text": response_data["text"],
            "links": [],  # No links in this simplified version
            "context": context
        }
    
    async def _handle_query(self, message: str, context: UserContext) -> Dict[str, Any]:
        """Handle travel queries using ChatGPT."""
        # Create a system prompt that provides context for the ChatGPT model
        system_prompt = {
            "role": "system", 
            "content": (
                "You are Jetzy, a knowledgeable and helpful travel assistant. "
                "Provide accurate, concise travel information with a friendly tone. "
                "When responding to travel queries:"
                "\n1. Focus on providing factual, current information"
                "\n2. Include specific details where possible (prices, times, locations, etc.)"
                "\n3. When making recommendations, provide brief reasons why"
                "\n4. Keep responses conversational but informative"
                "\n5. If you're unsure, be honest about limitations"
                "\n6. Suggest related travel considerations the user might not have thought about"
                "\n7. For pricing, use USD/EUR/local currency as appropriate"
                "\n8. Mention only one or two booking sites when relevant, like 'You can check prices on sites like Booking.com or Expedia'"
            )
        }
        
        # Create the messages array with system prompt and conversation history
        messages = [system_prompt]
        
        # Add relevant conversation history (limit to last 5 exchanges for context)
        history_limit = 10  # 5 exchanges (user & assistant)
        start_idx = max(0, len(context.conversation_history) - history_limit)
        messages.extend(context.conversation_history[start_idx:])
        
        # Get response from ChatGPT
        try:
            response = await self.chatgpt_client.generate_response(messages)
            
            # Extract the content from the response
            content = response.choices[0]["message"]["content"]
            
            return {
                "type": "general",
                "text": content
            }
        except Exception as e:
            # Handle API errors
            return {
                "type": "general",
                "text": "I'm having trouble connecting to my travel database at the moment. Please try again in a moment, or let me know if I can help with something else."
            }
    
    async def close(self):
        """Close all client connections."""
        await self.chatgpt_client.close()