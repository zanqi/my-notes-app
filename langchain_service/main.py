#!/usr/bin/env python3
"""
LangChain Service - Main Application
Provides AI chat functionality with RAG for the notes app
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from app.services.rag_service import RAGService
from app.services.vector_store_service import VectorStoreService
from app.models.chat_models import ChatRequest, ChatResponse, SyncNotesRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global service instances
rag_service = None
vector_store_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global rag_service, vector_store_service
    
    logger.info("Starting LangChain Service...")
    
    try:
        # Initialize services
        vector_store_service = VectorStoreService()
        await vector_store_service.initialize()
        
        rag_service = RAGService(vector_store_service)
        await rag_service.initialize()
        
        logger.info("Services initialized successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    finally:
        logger.info("Shutting down LangChain Service...")


# Create FastAPI app
app = FastAPI(
    title="LangChain Service",
    description="AI-powered chat service for notes using RAG",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Rails and Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "LangChain Service is running", "status": "healthy"}


@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        if not rag_service or not vector_store_service:
            raise HTTPException(status_code=503, detail="Services not initialized")
        
        # Test vector store connection
        collection_info = await vector_store_service.get_collection_info()
        
        return {
            "status": "healthy",
            "services": {
                "rag_service": "running",
                "vector_store": "running"
            },
            "collection_info": collection_info
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for AI conversations"""
    try:
        if not rag_service:
            raise HTTPException(status_code=503, detail="RAG service not initialized")
        
        logger.info(f"Processing chat request: {request.message[:100]}...")
        
        response = await rag_service.chat(
            message=request.message,
            conversation_id=request.conversation_id,
            include_sources=request.include_sources
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Chat request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.post("/sync_notes")
async def sync_notes(request: SyncNotesRequest):
    """Sync notes from Rails API to vector store"""
    try:
        if not vector_store_service:
            raise HTTPException(status_code=503, detail="Vector store service not initialized")
        
        logger.info(f"Syncing {len(request.notes)} notes to vector store")
        
        result = await vector_store_service.sync_notes(request.notes)
        
        return {
            "message": "Notes synced successfully",
            "processed": result["processed"],
            "total": result["total"]
        }
        
    except Exception as e:
        logger.error(f"Sync notes failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@app.post("/add_note")
async def add_note(note_data: dict):
    """Add a single note to the vector store"""
    try:
        if not vector_store_service:
            raise HTTPException(status_code=503, detail="Vector store service not initialized")
        
        logger.info(f"Adding note: {note_data.get('title', 'Untitled')}")
        
        result = await vector_store_service.add_note(note_data)
        
        return {
            "message": "Note added successfully",
            "note_id": result["note_id"]
        }
        
    except Exception as e:
        logger.error(f"Add note failed: {e}")
        raise HTTPException(status_code=500, detail=f"Add note failed: {str(e)}")


@app.delete("/notes/{note_id}")
async def delete_note(note_id: int):
    """Delete a note from the vector store"""
    try:
        if not vector_store_service:
            raise HTTPException(status_code=503, detail="Vector store service not initialized")
        
        logger.info(f"Deleting note: {note_id}")
        
        await vector_store_service.delete_note(note_id)
        
        return {"message": "Note deleted successfully"}
        
    except Exception as e:
        logger.error(f"Delete note failed: {e}")
        raise HTTPException(status_code=500, detail=f"Delete note failed: {str(e)}")


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history"""
    try:
        if not rag_service:
            raise HTTPException(status_code=503, detail="RAG service not initialized")
        
        history = await rag_service.get_conversation_history(conversation_id)
        
        return {
            "conversation_id": conversation_id,
            "messages": history
        }
        
    except Exception as e:
        logger.error(f"Get conversation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Get conversation failed: {str(e)}")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    ) 