# filepath: /home/jsust/Desktop/cropadvisor/src/models/chat_message.py
from pydantic import BaseModel

class ChatMessage(BaseModel):
    type: str = "text" 
    message: str = None
    base64: str = None