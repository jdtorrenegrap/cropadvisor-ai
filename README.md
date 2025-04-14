# CropAdvisor

CropAdvisor es un asistente de chat inteligente diseñado para apoyar a agricultores y técnicos en el monitoreo de cultivos. Integra modelos de IA conversacional y un módulo de visión por computadora con YOLO para el reconocimiento de posibles enfermedades en las plantas. Todo está orquestado mediante LangChain, y utiliza Redis Cloud para gestionar el historial de conversaciones.

Se conecta con la plataforma CROPS (Crop Resource Optimization Platform) para complementar la toma de decisiones agronómicas con datos relevantes y análisis automatizado.

## Clona este repositorio

```bash
git clone https://github.com/jdtorrenegrap/cropadvisor-ai.git
```

## Configuración del entorno Python

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows
```

```bash
 pip install -r requirements.txt
```

```bash
 uvicorn main:app --host 0.0.0.0 --port 8000
```
