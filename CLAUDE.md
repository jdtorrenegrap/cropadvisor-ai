# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CropAdvisor is an intelligent chat assistant for agricultural crop monitoring that integrates conversational AI with computer vision for disease detection. The system uses:

- **FastAPI** backend with streaming responses
- **LangChain** for AI orchestration
- **Google Gemini 2.0 Flash** as the primary LLM
- **YOLO models** for plant and disease detection
- **Redis Cloud** for conversation memory management
- **JWT token authentication** for user sessions

## Architecture

The codebase follows a service-oriented architecture:

### Core Components

- `main.py` - FastAPI application entry point with CORS middleware
- `src/routes/cropadvisor_chat.py` - Main chat endpoint with streaming responses
- `src/services/chat_service.py` - Central orchestration service that coordinates all AI components
- `src/services/memory_service.py` - Redis-based conversation memory using LangChain
- `src/services/detected_service.py` - YOLO model inference with Multiton pattern for model sharing
- `src/services/proxy.py` - Proxy pattern implementation for model detection
- `src/middleware/data_token.py` - JWT token validation and user extraction

### Key Design Patterns

- **Multiton Pattern**: Used in `ModelDetection` class to share YOLO model instances
- **Proxy Pattern**: `ModelDetectionProxy` wraps detection models
- **Service Layer**: Clean separation between routes, services, and core logic

### Data Flow

1. User sends message/image via `/cropadvisor/chat` endpoint
2. JWT token validated and user ID extracted
3. If image provided: YOLO models detect plants and diseases
4. Chat history retrieved from Redis
5. External data fetched (sensor reads, alerts) via `QueriesService`
6. Prompt constructed with context and detection results
7. Gemini model generates streaming response
8. Conversation saved to Redis memory

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Development server
uvicorn main:app --host 0.0.0.0 --port 8000

# Or using Python directly
python main.py

# Docker deployment
docker-compose up --build
```

### Environment Configuration

The application requires a `.env` file with:
- `llm` - Google Gemini API key
- Redis Cloud connection details (`host`, `redis_port`, `username`, `password`)
- External API endpoints for CROPS platform integration

## YOLO Models

Two pre-trained models are used:
- `src/models/best_plants.pt` - Plant detection (validates presence of plants)
- `src/models/best.pt` - Disease detection on detected plants

Detection threshold: 0.15 confidence for plant validation, 0.1 for disease detection.

## Testing

Test files are located in `test/` directory:
- `test/chat.py` - Chat service tests
- `test/memory.py` - Memory service tests
- `test/queries.py` - External API integration tests
- `test/fecha.py` - Date/time utility tests

No specific test runner is configured - tests appear to be standalone Python scripts.

## External Dependencies

The system integrates with the CROPS platform for:
- Sensor readings (`endpoint_get_read`)
- Alert configurations (`endpoint_alert_config`)
- Active alerts (`endpoint_alert_activated`)

These endpoints are configured via environment variables and accessed through `QueriesService`.