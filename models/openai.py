from typing import List, Optional, Dict, Any 
from pydantic import BaseModel, Field

class OpenaiRequest(BaseModel):

    model: str = Field(default="gpt-3.5-turbo")
    messages: List[Dict[str, str]]
    temperature: float = Field(default=0.7, ge=0, le=1)
    max_tokens: int = Field(default=1000, gt=0)
    top_p: float = Field(default=0.9, ge=0, le=1)
    frequency_penalty: float = Field(default=0.2, ge=0, le=2)
    presence_penalty: float = Field(default=0.4, ge=0, le=2)


class OpenaiResponse(BaseModel):

    id: str
    object: str
    created: List[Dict[str, Any]]
    usage: Dict[str, int]