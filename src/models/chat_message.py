from typing import Optional
from pydantic import BaseModel

class ChatMessage(BaseModel):
    type: str = "text"
    message: Optional[str] = None
    base64: Optional[str] = None