"""
Chat Models - Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User's message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    include_sources: bool = Field(True, description="Whether to include source notes in response")
    mode: Optional[str] = Field("traditional", description="RAG mode: 'traditional' or 'agent'")


class Source(BaseModel):
    """Source note information"""
    note_id: int = Field(..., description="ID of the source note")
    title: str = Field(..., description="Title of the source note")
    content_snippet: str = Field(..., description="Relevant content snippet")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    created_at: Optional[datetime] = Field(None, description="Note creation date")
    updated_at: Optional[datetime] = Field(None, description="Note last update date")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="AI-generated response")
    conversation_id: str = Field(..., description="Conversation ID")
    sources: List[Source] = Field(default_factory=list, description="Source notes used")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")


class Note(BaseModel):
    """Note model for syncing"""
    id: int = Field(..., description="Note ID")
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Note content")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    tags: List[str] = Field(default_factory=list, description="Note tags")
    category: Optional[str] = Field(None, description="Note category")


class SyncNotesRequest(BaseModel):
    """Request model for syncing notes"""
    notes: List[Note] = Field(..., description="List of notes to sync")


class ConversationMessage(BaseModel):
    """Individual message in a conversation"""
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")
    sources: List[Source] = Field(default_factory=list, description="Sources for assistant messages")


class ConversationHistory(BaseModel):
    """Conversation history model"""
    conversation_id: str = Field(..., description="Conversation ID")
    messages: List[ConversationMessage] = Field(..., description="List of messages")
    created_at: datetime = Field(..., description="Conversation creation time")
    updated_at: datetime = Field(..., description="Last update time") 