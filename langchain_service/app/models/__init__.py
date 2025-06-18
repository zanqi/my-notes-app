"""
Data models for the LangChain service.

This module contains Pydantic models for request/response validation
and data structures used throughout the application.
"""

from .chat_models import (
    ChatRequest,
    ChatResponse,
    Source,
    Note,
    SyncNotesRequest,
    ConversationMessage,
    ConversationHistory
)

__all__ = [
    "ChatRequest",
    "ChatResponse", 
    "Source",
    "Note",
    "SyncNotesRequest",
    "ConversationMessage",
    "ConversationHistory"
] 