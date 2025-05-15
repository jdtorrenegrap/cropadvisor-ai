from google import genai

client = genai.Client(api_key="AIzaSyDxcjO9Reb4PlIwy14GWoUCVk2Fa6PYpt8")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Hola"
)
print(response.text)
