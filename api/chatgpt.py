import httpx
import json
import traceback
import logging
from typing import List, Dict, Any, Optional
from models.openai import OpenaiRequest, OpenaiResponse
from config import settings

# Setup detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ChatGPTClient:
    """Client for interacting with the OpenAI API with improved error handling and debugging."""

    def __init__(self):
        logger.info("Initializing ChatGPTClient")
        try:
            # Get the API key from settings
            self.api_key = settings.openai_api_key
            if not self.api_key:
                logger.error("OpenAI API key is missing or empty")
                raise ValueError("OpenAI API key is missing or empty")
                
            # Log a masked version of the key for verification
            masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}" if len(self.api_key) > 8 else "***"
            logger.info(f"Using OpenAI API key: {masked_key}")
            
            self.base_url = "https://api.openai.com/v1"
            
            # Initialize HTTP client with longer timeout
            self.client = httpx.AsyncClient(
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30.0 
            )
            
            logger.info("ChatGPTClient initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ChatGPTClient: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            raise

    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate a response from OpenAI with comprehensive error handling."""
        logger.info(f"Generating response for {len(messages)} messages")
        
        # Get model or use default
        model = kwargs.get("model", settings.default_model)
        logger.info(f"Using model: {model}")
        
        # First try with the specified model
        try:
            return await self._make_api_request(messages, model, **kwargs)
        except Exception as e:
            logger.warning(f"Error with model {model}: {str(e)}")
            
           
            fallback_model = "gpt-3.5-turbo-0125"
            if model != fallback_model:
                logger.info(f"Trying fallback model: {fallback_model}")
                try:
                    return await self._make_api_request(messages, fallback_model, **kwargs)
                except Exception as fallback_e:
                    logger.error(f"Fallback to {fallback_model} also failed: {str(fallback_e)}")
            
            
            try:
                logger.info("Trying generic gpt-3.5-turbo as final fallback")
                return await self._make_api_request(messages, "gpt-3.5-turbo", **kwargs)
            except Exception as final_e:
                logger.error(f"All fallback attempts failed: {str(final_e)}")
                raise e 
    
    async def _make_api_request(self, messages: List[Dict[str, str]], model: str, **kwargs) -> Dict[str, Any]:
        """Make the actual API request with detailed logging."""
        try:
            # Prepare request data
            request_data = OpenaiRequest(
                model=model,
                messages=messages,
                temperature=kwargs.get("temperature", settings.default_temperature),
                max_tokens=kwargs.get("max_tokens", settings.default_max_tokens),
                top_p=kwargs.get("top_p", settings.default_top_p),
                frequency_penalty=kwargs.get("frequency_penalty", settings.default_frequency_penalty),
                presence_penalty=kwargs.get("presence_penalty", settings.default_presence_penalty)
            )
            
           
            sanitized_request = {
                "model": request_data.model,
                "message_count": len(request_data.messages),
                "temperature": request_data.temperature,
                "max_tokens": request_data.max_tokens
            }
            logger.info(f"Sending request to OpenAI API: {sanitized_request}")
            
            
            request_dict = request_data.dict()
            
            # Send the request
            logger.debug("Sending API request...")
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=request_dict
            )
            
            
            response.raise_for_status()
            
            
            response_data = response.json()
            
            sanitized_response = {
                "id": response_data.get("id", "unknown"),
                "model": response_data.get("model", "unknown"),
                "choices_count": len(response_data.get("choices", [])),
                "usage": response_data.get("usage", {})
            }
            logger.info(f"Received response from OpenAI API: {sanitized_response}")
            
            
            return response_data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.TimeoutException:
            logger.error(f"Request timed out for model {model}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error for model {model}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error with model {model}: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            raise
    
    async def close(self):
        """Close the HTTP client session."""
        try:
            logger.info("Closing HTTP client")
            await self.client.aclose()
            logger.info("HTTP client closed")
        except Exception as e:
            logger.error(f"Error closing HTTP client: {str(e)}")


# Simple test function to verify the client works
async def test_client():
    """Test the ChatGPT client with a simple message."""
    import asyncio
    
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Starting test client")
    client = ChatGPTClient()
    
    try:
        logger.info("Sending test message")
        response = await client.generate_response([
            {"role": "system", "content": "You are a helpful travel assistant."},
            {"role": "user", "content": "Hello, can you suggest a good place to visit in Europe?"}
        ])
        
        logger.info("Received response")
        
        if "choices" in response and len(response["choices"]) > 0:
            content = response["choices"][0]["message"]["content"]
            logger.info(f"Response content: {content[:100]}...")
            print(f"\nResponse from OpenAI API: {content}")
        else:
            logger.warning(f"Unexpected response format: {response}")
            print(f"Unexpected response format")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        print(f"Test failed: {str(e)}")
    finally:
        logger.info("Closing client")
        await client.close()
        logger.info("Test completed")

if __name__ == "__main__":
    asyncio.run(test_client())