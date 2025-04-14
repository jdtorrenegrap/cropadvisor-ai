import os
import cv2
import base64
import numpy as np
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

        self.model = ChatDeepSeek(
            model_name="deepseek-chat",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=os.getenv("llm")
        )

        self.prompt_template = ChatPromptTemplate.from_messages([
            (
                "system",
                """Eres Senda, un asistente agrícola experto en monitoreo de cultivos. Estás conectado al sistema CROP (Crop Resource Optimization Platform).

                Ayuda a los agricultores con información clara y útil sobre sus cultivos, basándote en:
                - Lecturas de sensores: {reads}  
                - Alertas configuradas: {alerts}  
                - Alertas activadas: {alerts_activated}  
                - Historial de conversación: {chat_history}  

                - Explica de manera simple y clara lo que indican las lecturas.  
                - Si hay alertas activadas, menciónalas y explica qué acción se recomienda.  
                - Si no hay alertas, ofrece recomendaciones de monitoreo o prevención.  
                - Usa ejemplos o comparaciones prácticas cuando sea útil.  

                - Ten en cuenta el rango de error de los sensores.  
                - No inventes información si algún dato falta.  
 
                Responde con un tono amigable y relajado, como un buen compañero de campo.  
                Solo responde preguntas agrícolas. Si la pregunta no es relevante, responde de forma educada sin desviarte del tema.  
                Si dices "Hola" al inicio no es necesario que lo repitas en cada respuesta.

                ¡Vamos a ayudar a nuestros agricultores!
                """
            ),
            ("human", "**Pregunta:** {question}")
        ])

    def chat(self, token, message):
        try:
            user_id = self.data_token.extract_user_info(token)[0]
            chat_history = self.memory.get_chat_history(user_id)

            reads = self.queries_service.get_reads(token)
            alerts = self.queries_service.get_alerts(token)
            alerts_activated = self.queries_service.get_alerts_activated(token)

            if isinstance(message, dict) and message.get("type") == "image":
                image_b64 = message["base64"]
                image_bytes = base64.b64decode(image_b64)
                nparr = np.frombuffer(image_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                detections = self.model_detection.detect(img)

                img_with_boxes = self.model_detection.draw_boxes(img.copy(), detections[0])
                img_encoded = self.model_detection.encode_image(img_with_boxes)

                detections_summary = (
                    "\n".join(
                        f"{d['class_name']} ({d['confidence']*100:.1f}%)"
                        for d in detections[0]
                    )
                    if detections[0] else "No se detectaron enfermedades visibles."
                )

                message = f"Se detectaron: {detections_summary}. ¿Qué recomendaciones puedes dar?"

                input_data = {
                    "chat_history": chat_history,
                    "question": message,
                    "reads": reads,
                    "alerts": alerts,
                    "alerts_activated": alerts_activated
                }

                prompt = self.prompt_template.format_prompt(**input_data)
                response = self.model.invoke(prompt)

                response_text = (
                    response.get("content") if isinstance(response, dict)
                    else getattr(response, "content", "No se pudo generar una respuesta.")
                )

                cleaned_message = (message.get("message") if isinstance(message, dict) else message)
                self.memory.save_message(user_id, cleaned_message, response_text)

                return {
                    "message": response_text,
                    "image": f"data:image/jpeg;base64,{img_encoded}"
                }

            else:
                input_data = {
                    "chat_history": chat_history,
                    "question": message,
                    "reads": reads,
                    "alerts": alerts,
                    "alerts_activated": alerts_activated
                }

                prompt = self.prompt_template.format_prompt(**input_data)
                response = self.model.invoke(prompt)

                response_text = (
                    response.get("content") if isinstance(response, dict)
                    else getattr(response, "content", "No se pudo generar una respuesta.")
                )

                cleaned_message = (message.get("message") if isinstance(message, dict) else message)
                self.memory.save_message(user_id, cleaned_message, response_text)

                return {
                    "message": response_text,
                    "image": None
                }

        except Exception as e:
            return {"message": f"Lo siento, ocurrió un error: {str(e)}", "image": None}