import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_url = "http://127.0.0.1:8000/cropadvisor/chat"  # URL del endpoint de la API
test_token = os.getenv("TEST_TOKEN")

print("IA-> Bienvenido al chatbot de monitoreo de cultivos.")
print("Escribe 'salir' para terminar la conversación.\n")

while True:
    user_message = input("Tú: ")
    
    if user_message.lower() == "salir":
        print("¡Hasta luego!")
        break

    try:
        # Enviar la solicitud POST a la API
        headers = {"Authorization": f"Bearer {test_token}"}
        payload = {"message": user_message}
        response = requests.post(api_url, json=payload, headers=headers, stream=True)

        # Verificar si la respuesta es exitosa
        if response.status_code == 200:
            print("IA-> Chatbot: ", end="", flush=True)
            for chunk in response.iter_content(chunk_size=1024):
                print(chunk.decode("utf-8"), end="", flush=True)
            print("\n")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")
        break