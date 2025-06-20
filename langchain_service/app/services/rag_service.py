"""
RAG Service - Handles AI chat functionality with context retrieval
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
import uuid
from datetime import datetime

from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory

from ..models.chat_models import ChatResponse, Source, ConversationMessage
from .vector_store_service import VectorStoreService

logger = logging.getLogger(__name__)


class RAGService:
    """Service for handling RAG-based AI conversations"""
    
    def __init__(self, vector_store_service: VectorStoreService, use_langgraph: Optional[bool] = None):
        self.vector_store_service = vector_store_service
        self.llm = None
        self.conversations = {}  # In-memory conversation storage
        self.max_context_notes = 5
        self.conversation_window = 10  # Keep last 10 messages
        # Allow override via parameter, otherwise check environment variable
        if use_langgraph is not None:
            self.use_langgraph = use_langgraph
        else:
            self.use_langgraph = os.getenv("USE_LANGGRAPH", "false").lower() in ("true", "1", "yes")
        self.langgraph_service = None
        
    async def initialize(self):
        """Initialize the RAG service"""
        try:
            if self.use_langgraph:
                # Initialize LangGraph service
                try:
                    from .langgraph_rag_service import LangGraphRAGService
                    self.langgraph_service = LangGraphRAGService(self.vector_store_service)
                    await self.langgraph_service.initialize()
                    logger.info("RAG service initialized with LangGraph")
                except ImportError as e:
                    logger.warning(f"LangGraph dependencies not available: {e}")
                    logger.info("Falling back to traditional RAG")
                    self.use_langgraph = False
            
            if not self.use_langgraph:
                # Initialize OpenAI LLM for traditional RAG
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY environment variable is required")
                
                model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
                temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
                
                # Try different initialization approaches for compatibility
                try:
                    self.llm = ChatOpenAI(
                        api_key=SecretStr(api_key),
                        model=model_name,
                        temperature=temperature
                    )
                    logger.info(f"RAG service initialized with SecretStr approach, model: {model_name}")
                except Exception as e:
                    logger.warning(f"SecretStr initialization failed: {e}, trying alternative approach")
                    try:
                        # Alternative approach without SecretStr
                        os.environ["OPENAI_API_KEY"] = api_key
                        self.llm = ChatOpenAI(
                            model=model_name,
                            temperature=temperature
                        )
                        logger.info(f"RAG service initialized with environment variable approach, model: {model_name}")
                    except Exception as e2:
                        logger.error(f"Both initialization approaches failed: {e2}")
                        raise e2
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise
    
    def _create_system_prompt(self, sources: List[Source]) -> str:
        """Create system prompt with context from relevant notes"""
        
        base_prompt = """You are an AI assistant helping users find and discuss information from their personal notes. 

Your role:
- Answer questions based on the provided note context
- Be helpful, accurate, and conversational
- If the context doesn't contain enough information, say so honestly
- Always cite which notes you're referencing when possible
- Summarize and synthesize information from multiple notes when relevant

Guidelines:
- Be concise but thorough
- Use a friendly, personal tone since these are the user's own notes
- If asked about something not in the notes, clarify that you can only work with the provided notes
- When referencing notes, mention the note title when possible"""

        if sources:
            context_text = "\n\nRelevant notes context:\n"
            for i, source in enumerate(sources, 1):
                context_text += f"\n{i}. Note: \"{source.title}\"\n"
                context_text += f"   Content: {source.content_snippet}\n"
                context_text += f"   Relevance: {source.relevance_score:.2f}\n"
            
            return base_prompt + context_text
        else:
            return base_prompt + "\n\nNo relevant notes were found for this query. Let the user know that you don't have information about this topic in their notes."
    
    def _get_or_create_conversation(self, conversation_id: Optional[str]) -> str:
        """Get existing conversation or create new one"""
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {
                "messages": [],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        
        return conversation_id
    
    def _add_message_to_conversation(self, conversation_id: str, role: str, content: str, sources: Optional[List[Source]] = None):
        """Add a message to conversation history"""
        if conversation_id in self.conversations:
            message = ConversationMessage(
                role=role,
                content=content,
                timestamp=datetime.now(),
                sources=sources or []
            )
            
            self.conversations[conversation_id]["messages"].append(message)
            self.conversations[conversation_id]["updated_at"] = datetime.now()
            
            # Keep only recent messages to prevent memory overflow
            if len(self.conversations[conversation_id]["messages"]) > self.conversation_window * 2:
                # Keep last conversation_window*2 messages (user + assistant pairs)
                self.conversations[conversation_id]["messages"] = \
                    self.conversations[conversation_id]["messages"][-self.conversation_window * 2:]
    
    def _get_conversation_context(self, conversation_id: str) -> List[Any]:
        """Get recent conversation messages for context"""
        if conversation_id not in self.conversations:
            return []
        
        messages = []
        recent_messages = self.conversations[conversation_id]["messages"][-self.conversation_window:]
        
        for msg in recent_messages:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
        
        return messages
    
    async def chat(self, message: str, conversation_id: Optional[str] = None, include_sources: bool = True) -> ChatResponse:
        """Handle a chat request with RAG"""
        try:
            # Route to appropriate service based on configuration
            if self.use_langgraph and self.langgraph_service:
                return await self.langgraph_service.chat(message, conversation_id, include_sources)
            else:
                return await self._traditional_chat(message, conversation_id, include_sources)
            
        except Exception as e:
            logger.error(f"Chat request failed: {e}")
            raise
    
    async def _traditional_chat(self, message: str, conversation_id: Optional[str] = None, include_sources: bool = True) -> ChatResponse:
        """Handle a chat request with traditional RAG approach"""
        # Get or create conversation
        conv_id = self._get_or_create_conversation(conversation_id)
        
        # Add user message to conversation
        self._add_message_to_conversation(conv_id, "user", message)
        
        # Search for relevant notes
        sources = []
        if include_sources:
            sources = await self.vector_store_service.search_similar_notes(
                query=message, 
                n_results=self.max_context_notes
            )
            # Filter sources with low relevance scores
            sources = [s for s in sources if s.relevance_score > 0.3]
        
        # Create system prompt with context
        system_prompt = self._create_system_prompt(sources)
        
        # Get conversation history
        conversation_history = self._get_conversation_context(conv_id)
        
        # Prepare messages for LLM
        messages: List[Union[SystemMessage, HumanMessage, AIMessage]] = [SystemMessage(content=system_prompt)]
        messages.extend(conversation_history)
        messages.append(HumanMessage(content=message))
        
        # Generate response
        logger.info(f"Generating response for conversation {conv_id}")
        if not self.llm:
            raise ValueError("LLM not initialized")
        response = await self.llm.ainvoke(messages)
        response_text = response.content if isinstance(response.content, str) else str(response.content)
        
        # Add assistant response to conversation
        self._add_message_to_conversation(conv_id, "assistant", response_text, sources)
        
        # Calculate tokens used (approximate)
        total_text = system_prompt + message + response_text
        tokens_used = len(total_text.split()) * 1.3  # Rough estimate
        
        return ChatResponse(
            response=response_text,
            conversation_id=conv_id,
            sources=sources,
            timestamp=datetime.now(),
            tokens_used=int(tokens_used)
        )
    
    async def get_conversation_history(self, conversation_id: str) -> List[ConversationMessage]:
        """Get conversation history"""
        if self.use_langgraph and self.langgraph_service:
            return await self.langgraph_service.get_conversation_history(conversation_id)
        
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]["messages"]
        return []
    
    async def clear_conversation(self, conversation_id: str):
        """Clear a conversation"""
        if self.use_langgraph and self.langgraph_service:
            return await self.langgraph_service.clear_conversation(conversation_id)
        
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Cleared conversation {conversation_id}")
    
    async def get_all_conversations(self) -> Dict[str, Any]:
        """Get all conversation IDs and metadata"""
        if self.use_langgraph and self.langgraph_service:
            return await self.langgraph_service.get_all_conversations()
        
        result = {}
        for conv_id, conv_data in self.conversations.items():
            result[conv_id] = {
                "created_at": conv_data["created_at"],
                "updated_at": conv_data["updated_at"],
                "message_count": len(conv_data["messages"])
            }
        return result
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        if self.use_langgraph and self.langgraph_service:
            return self.langgraph_service.get_service_stats()
        
        total_conversations = len(self.conversations)
        total_messages = sum(len(conv["messages"]) for conv in self.conversations.values())
        
        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "max_context_notes": self.max_context_notes,
            "conversation_window": self.conversation_window,
            "model": getattr(self.llm, 'model_name', 'Unknown') if self.llm else 'Not initialized',
            "service_type": "traditional"
        } 