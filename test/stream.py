import os
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente agrícola experto en cultivos."),
    ("human", "¿Cuál es la mejor hora para regar tomates?")
])


model = ChatDeepSeek(
    model_name="deepseek-chat",
    temperature=0.7,
    streaming=True, 
    api_key=os.getenv("llm")  
)


print("Respuesta del modelo:")
for chunk in model.stream(prompt.format_prompt()):
    print(chunk.content, end="", flush=True)