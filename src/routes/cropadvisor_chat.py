from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from src.services.chat_service import ChatService
from src.models.chat_message import ChatMessage
from src.middleware.data_token import TokenUsers

router = APIRouter()
chat = ChatService()

@router.post("/cropadvisor/chat")
async def chat_message(message: ChatMessage, token: str = Depends(TokenUsers.validate_token)):
    try:
        generator = chat.chat(token, message.dict())
        return StreamingResponse(generator, media_type="text/plain")  
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
