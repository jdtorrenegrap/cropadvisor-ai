FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

#Dependencies del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
# Copiar el archivo requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar el codigo de la aplicación
COPY . .

# Esto es el punto de entrada de la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["python", "main.py"]