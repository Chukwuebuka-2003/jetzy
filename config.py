from pydantic import Field
from pydantic_settings import BaseSettings

from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    openai_api_key: str = Field(default="mock-key", env="OPENAI_API_KEY")

    default_model: str = "gpt-3.5-turbo"
    default_temperature: float = 0.7
    default_max_tokens: int = 1000
    default_top_p: float = 0.2
    default_frequency_penalty: float = 0.2
    default_presence_penalty: float = 0.3

    # External APIs that will be integrated
    skyscanner_api_key: str = Field(default="mock-key", env="SKYSCANNER_API_KEY")
    expedia_api_key: str = Field(default="mock-key", env="EXPEDIA_API_KEY")
    booking_api_key: str = Field(default="mock-key", env="BOOKING_API_KEY")
    hotels_api_key: str = Field(default="mock-key", env="HOTELS_API_KEY")
    tripadvisor_api_key: str = Field(default="mock-key", env="TRIPADVISOR_API_KEY")
    google_maps_api_key: str = Field(default="mock-key", env="GOOGLE_MAPS_API_KEY")
    yelp_api_key: str = Field(default="mock-key", env="YELP_API_KEY") 
    zomato_api_key: str = Field(default="mock-key", env="ZOMATO_API_KEY")
    rome2rio_api_key: str = Field(default="mock-key", env="ROME2RIO_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()