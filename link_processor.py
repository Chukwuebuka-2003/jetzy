import re
from typing import List, Dict, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkProcessor:
    """
    Processes and formats travel links in AI responses.
    
    This class handles the extraction and formatting of travel-related links
    in AI responses, ensuring they are properly presented to users.
    """
    
    @staticmethod
    def extract_links(text: str) -> List[Dict[str, str]]:
        """
        Extract links from response text.
        
        Args:
            text: The text to extract links from.
            
        Returns:
            A list of dictionaries containing link data (url and display text).
        """
        links = []
        
        try:
           
            generic_link_pattern = r'<Links to ([^>]+)>'
            generic_matches = re.findall(generic_link_pattern, text)
            
            for purpose in generic_matches:
                links.append({
                    "url": LinkProcessor._generate_placeholder_url(purpose),
                    "text": f"Find {purpose}",
                    "type": "general"
                })
            
            specific_link_pattern = r'<link:(.*?)\|(.*?)>'
            specific_matches = re.findall(specific_link_pattern, text)
            
            for url, display_text in specific_matches:
                links.append({
                    "url": url,
                    "text": display_text,
                    "type": "specific"
                })
            
            if "places to visit" in text.lower() or "attractions" in text.lower():
                # Extract location if possible
                location_pattern = r'in ([A-Za-z\s]+)[\.\,]'
                location_match = re.search(location_pattern, text)
                location = location_match.group(1) if location_match else "the area"
                
                # Extract mentioned places
                places = []
                place_pattern = r'((?:[A-Z][a-z]+\s*)+)(?:\(|\,|\s+and\s+|\.|\s+is)'
                place_matches = re.findall(place_pattern, text)
                
                # Clean up the matches
                for place in place_matches:
                    place = place.strip()
                    if len(place) > 3 and place not in ["New York", "United States", "America"]:
                        places.append(place)
                
                # Generate links for places
                for place in places[:3]:  # Limit to 3 places
                    links.append({
                        "url": f"https://www.google.com/search?q={place}+{location}",
                        "text": f"Learn about {place}",
                        "type": "attraction"
                    })
                
                # Add a generic "explore" link
                links.append({
                    "url": f"https://www.google.com/search?q=things+to+do+in+{location.replace(' ', '+')}",
                    "text": f"Explore {location}",
                    "type": "general"
                })
            
            return links
        except Exception as e:
            logger.error(f"Error extracting links: {str(e)}")
            return []
    
    @staticmethod
    def _generate_placeholder_url(purpose: str) -> str:
        """
        Generate a placeholder URL for generic link purposes.
        
        Args:
            purpose: The purpose of the link (e.g., "book flights").
            
        Returns:
            A placeholder URL.
        """
        purpose_lower = purpose.lower().strip()
        
        if "flight" in purpose_lower:
            return "https://www.skyscanner.com/"
        elif "hotel" in purpose_lower:
            return "https://www.booking.com/"
        elif "restaurant" in purpose_lower or "dining" in purpose_lower or "reservation" in purpose_lower:
            return "https://www.opentable.com/"
        elif "attraction" in purpose_lower or "place" in purpose_lower or "these places" in purpose_lower:
            return "https://www.tripadvisor.com/"
        elif "transport" in purpose_lower:
            return "https://www.rome2rio.com/"
        else:
            return "https://www.google.com/travel"
    
    @staticmethod
    def format_response_with_links(text: str) -> str:
        """
        Format the response text by cleaning up link notations.
        
        Args:
            text: The response text containing link notations.
            
        Returns:
            The formatted text with clean link references.
        """
        # Replace Format 1 links (<Links to book flights>)
        # We'll keep the generic link text as a signal to the user that links are available
        
        # Replace Format 2 links (<link:URL|Text>)
        text = re.sub(r'<link:(.*?)\|(.*?)>', r'\2', text)
        
        return text
    
    @staticmethod
    def generate_booking_links(data_type: str, data: Dict) -> List[Dict[str, str]]:
        """
        Generate booking links based on the data type and content.
        
        Args:
            data_type: The type of data (flight, hotel, etc.).
            data: The data containing booking information.
            
        Returns:
            A list of booking links.
        """
        links = []
        
        if data_type == "flight" and data and "options" in data:
            for i, option in enumerate(data["options"][:3]):  # Limit to first 3 options
                airline = option["outbound_segments"][0]["airline"]
                price = f"${option['total_price']}"
                links.append({
                    "url": option.get("booking_link", "https://www.skyscanner.com/"),
                    "text": f"Book {airline} flight for {price}",
                    "type": "booking"
                })
        
        elif data_type == "restaurant" and data and "options" in data:
            for i, option in enumerate(data["options"][:3]):  # Limit to first 3 options
                links.append({
                    "url": option.get("reservation_link", "https://www.opentable.com/"),
                    "text": f"Reserve a table at {option['name']}",
                    "type": "booking"
                })
        
        elif data_type == "attraction" and data and "attractions" in data:
            for i, attraction in enumerate(data["attractions"][:3]):  # Limit to first 3 options
                location = data.get("location", "")
                links.append({
                    "url": f"https://www.google.com/search?q={attraction['name']}+{location}",
                    "text": f"Visit {attraction['name']}",
                    "type": "attraction"
                })
        
        elif data_type == "transport" and data and "options" in data:
            for i, option in enumerate(data["options"][:3]):  # Limit to first 3 options
                mode = option["segments"][0]["mode"]
                price = f"${option['total_price']}"
                links.append({
                    "url": option.get("booking_link", "https://www.rome2rio.com/"),
                    "text": f"Book {mode} for {price}",
                    "type": "booking"
                })
        
        return links