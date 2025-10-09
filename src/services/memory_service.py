# from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
# from src.core.config import Settings
from datetime import datetime

class MemoryService:
    def __init__(self):
        # TODO: Implementar cache con Redis
        # self.redis_url = Settings.REDIS_URL
        self.memory = {}

    def get_user_memory(self, user_id: str):
        """Obtenemos la memoria del usuario en memoria local (sin Redis)."""
        user_id = str(user_id)

        if user_id not in self.memory:
            # TODO: Conectar con Redis para persistencia
            # self.memory[user_id] = RedisChatMessageHistory(
            #     session_id=user_id,
            #     url=self.redis_url
            # )
            self.memory[user_id] = []
        return self.memory[user_id]

    def save_message(self, user_id: str, user_message: str, response_ia: str):
        """Guarda los mensajes en memoria local con timestamp."""
        memory = self.get_user_memory(user_id)
        timestamp = datetime.now().isoformat()

        # TODO: Cuando se implemente Redis, usar add_message
        memory.append(HumanMessage(
            content=user_message,
            additional_kwargs={"timestamp": timestamp}
        ))
        memory.append(AIMessage(
            content=response_ia,
            additional_kwargs={"timestamp": timestamp}
        ))

    def get_chat_history(self, user_id: str):
        """Obtiene el historial del chat del usuario."""
        memory = self.get_user_memory(user_id)
        return memory if memory else []
