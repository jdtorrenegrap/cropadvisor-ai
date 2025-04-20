import os
import cv2
import base64
import numpy as np
from datetime import datetime
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
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
        self.model_detection = ModelDetection(model_path='src/models/best.pt')
        self.model_detection_plant = ModelDetection(model_path='src/models/best_plants.pt')

        self.model = ChatDeepSeek(
            model_name="deepseek-chat",
            temperature=0.7,
            streaming=True,
            api_key=os.getenv("llm")
        )

        self.prompt_template = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are Senda, an agricultural assistant expert in crop monitoring. You are connected to the CROP (Crop Resource Optimization Platform) system.

                You help farmers with clear and useful information about their crops, based on:
                - Sensor readings: {reads} 
                - Configured alerts: {alerts} 
                - Chat history: {chat_history} 
                - Current date: {datetime_now}

                - Explain simply and clearly what the readings indicate.    
                - If alerts are enabled, mention them and explain what action is recommended.    
                - If there are no alerts, offer recommendations for monitoring or prevention.  

                - Take into account the error range of the sensors.   
                - Don't make up information if any data is missing.  
 
                 Respond like a good field partner.    
                 Only answer agricultural questions. If the question is not relevant, answer politely and stay on topic.  
                 Say "Hello" at the beginning, and don't repeat it in every answer.

                """
            ),
            ("human", "**Question:** {question}")
        ])

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
                image_b64 = message["base64"]
                if not image_b64 == message.get("base64"):
                    raise ValueError("No se proporcionó una imagen válida.")
                
                image_bytes = base64.b64decode(image_b64)
                nparr = np.frombuffer(image_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                plant_detections = self.model_detection_plant.detect(img)
                print("Debug: ", plant_detections)
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

            prompt = self.prompt_template.format_prompt(**input_data)
            full_response = ""

            for chunk in self.model.stream(prompt):
                content = chunk.content if hasattr(chunk, "content") else str(chunk)
                full_response += content
                yield content

            if not full_response.strip():
                full_response = "Lo siento, no tengo información para responder a tu pregunta."
            
            cleaned_message = (message.get("message") if isinstance(message, dict) else message)
            self.memory.save_message(user_id, cleaned_message, full_response)

            return {
                "message": full_response,
                "image": None
            }

        except Exception as e:
            return {"message": f"Lo siento, ocurrió un error: {str(e)}", "image": None}