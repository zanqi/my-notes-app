# LangChain Service

Python microservice for AI chat functionality using LangChain and OpenAI.

## Structure

```
langchain_service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models/              # Data models
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── Dockerfile              # Docker configuration
└── start.sh                # Startup script
```

## Purpose

This service handles:
- Note embedding generation and storage
- Vector similarity search
- AI chat responses using RAG (Retrieval Augmented Generation)
- Integration with Rails API via HTTP endpoints

## API Endpoints

- `GET /health` - Health check
- `POST /sync_note` - Sync note embeddings
- `POST /chat` - Process chat messages 