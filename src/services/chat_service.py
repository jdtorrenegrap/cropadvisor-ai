import os
import cv2
import base64
import numpy as np
from datetime import datetime
from langchain_deepseek import ChatDeepSeek
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.services.promt_service import PromptService
from src.services.proxy import ModelDetectionProxy
from src.services.queries_service import QueriesService
from src.services.memory_service import MemoryService
from src.middleware.data_token import TokenUsers
from src.services.detected_service import ModelDetection

load_dotenv()

class ChatService:

    def __init__(self):

        self.memory = MemoryService()
        self.data_token = TokenUsers()
        self.queries_service = QueriesService()
        self.prompt_service = PromptService()
        
        self.model_detection = ModelDetectionProxy(ModelDetection(model_path='src/models/best.pt'))
        self.model_detection_plant = ModelDetectionProxy(ModelDetection(model_path='src/models/best_plants.pt'))
   
        self.model = ChatGoogleGenerativeAI(
              model="gemini-2.0-flash",
              temperature=0,
              disable_streaming=True,
              max_tokens=None,
              timeout=None,
              max_retries=2, 
              api_key=os.getenv("llm")
             )

    def chat(self, token, message):

        try:

            user_id = self.data_token.extract_user_info(token)[0]
            chat_history = self.memory.get_chat_history(user_id)
            
            reads = self.queries_service.get_reads(token)
            alerts = self.queries_service.get_alerts(token)
            alerts_activated = self.queries_service.get_alerts_activated(token)

            datetime_now = datetime.today().strftime("%Y-%m-%d")
            detections_summary = None 

            if isinstance(message, dict) and message.get("type") == "image":
                image_b64 = message.get("base64")
                if not image_b64:
                    raise ValueError("No se proporcionó una imagen válida.")
                
                image_bytes = base64.b64decode(image_b64)
                nparr = np.frombuffer(image_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                plant_detections = self.model_detection_plant.detect(img)
                validate_detections = ['plants']
                threshold = 0.15

                plant_detections = any(
                    d['class_name'] in validate_detections and d['confidence'] >= threshold
                    for d in plant_detections[0]
                )
                if not plant_detections:
                    yield "No se detectaron plantas en la imagen."
                    return {"message": "No se detectaron plantas en la imagen.", "image": None}
                
                detections = self.model_detection.detect(img)
                detections_summary = (
                    "\n".join(
                        f"{d['class_name']} ({d['confidence']*100:.1f}%)"
                        for d in detections[0]
                    )
                    if detections[0] else "No se detectaron enfermedades visibles."
                )

                message["message"] = f"{detections_summary}. {message.get('message')}"

                if not message.get("message"):
                   message["message"] = f"Se detectaron: {detections_summary}. ¿Qué recomendaciones puedes dar?"
            
            input_data = {
                "chat_history": chat_history,
                "question": message.get("message", "") if isinstance(message, dict) else message,
                "imge": detections_summary if detections_summary else "No se proporcionó imagen.",
                "reads": reads,
                "alerts": alerts,
                "alerts_activated": alerts_activated,
                "datetime_now": datetime_now
            }

            prompt = self.prompt_service.create_prompt(**input_data)
            full_response = ""
            
            for chunk in self.model.stream(prompt):
                content = chunk.content if hasattr(chunk, "content") else str(chunk)
                full_response += content 
                yield content

            cleaned_message = (message.get("message") if isinstance(message, dict) else message)
            self.memory.save_message(user_id, cleaned_message, full_response)

        except Exception as e:
            yield{"message": f"Lo siento, ocurrió un error: {str(e)}", "image": None}