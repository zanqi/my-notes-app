"""
Vector Store Service - Manages ChromaDB for note embeddings
"""

import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import uuid
from datetime import datetime

from ..models.chat_models import Note, Source

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for managing vector storage and retrieval of notes"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.embeddings_model = None
        self.collection_name = "notes_collection"
        
    async def initialize(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Initialize ChromaDB client
            persist_directory = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
            os.makedirs(persist_directory, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Initialize embeddings model
            model_name = os.getenv("EMBEDDINGS_MODEL", "all-MiniLM-L6-v2")
            logger.info(f"Loading embeddings model: {model_name}")
            self.embeddings_model = SentenceTransformer(model_name)
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                logger.info(f"Using existing collection: {self.collection_name}")
            except ValueError:
                # Collection doesn't exist, create it
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Notes embeddings for RAG"}
                )
                logger.info(f"Created new collection: {self.collection_name}")
            
            logger.info("Vector store service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store service: {e}")
            raise
    
    def _create_document_id(self, note_id: int) -> str:
        """Create a unique document ID from note ID"""
        return f"note_{note_id}"
    
    def _prepare_note_text(self, note: Note) -> str:
        """Prepare note text for embedding"""
        # Combine title and content for better context
        text_parts = [note.title]
        if note.content.strip():
            text_parts.append(note.content)
        if note.tags:
            text_parts.append(f"Tags: {', '.join(note.tags)}")
        if note.category:
            text_parts.append(f"Category: {note.category}")
        
        return "\n\n".join(text_parts)
    
    async def add_note(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a single note to the vector store"""
        try:
            # Convert dict to Note model
            note = Note(**note_data)
            
            # Prepare text and generate embedding
            text = self._prepare_note_text(note)
            embedding = self.embeddings_model.encode(text).tolist()
            
            # Create document ID
            doc_id = self._create_document_id(note.id)
            
            # Prepare metadata (ChromaDB only accepts primitive types)
            metadata = {
                "note_id": note.id,
                "title": note.title,
                "created_at": note.created_at.isoformat(),
                "updated_at": note.updated_at.isoformat(),
                "tags": ", ".join(note.tags) if note.tags else "",  # Convert list to string
                "category": note.category or "",
                "content_length": len(note.content)
            }
            
            # Check if document already exists
            existing = self.collection.get(ids=[doc_id])
            
            if existing['ids']:
                # Update existing document
                self.collection.update(
                    ids=[doc_id],
                    embeddings=[embedding],
                    metadatas=[metadata],
                    documents=[text]
                )
                logger.info(f"Updated note {note.id} in vector store")
            else:
                # Add new document
                self.collection.add(
                    ids=[doc_id],
                    embeddings=[embedding],
                    metadatas=[metadata],
                    documents=[text]
                )
                logger.info(f"Added note {note.id} to vector store")
            
            return {"note_id": note.id, "status": "success"}
            
        except Exception as e:
            logger.error(f"Failed to add note to vector store: {e}")
            raise
    
    async def sync_notes(self, notes: List[Note]) -> Dict[str, Any]:
        """Sync multiple notes to the vector store"""
        try:
            processed = 0
            errors = []
            
            for note in notes:
                try:
                    await self.add_note(note.dict())
                    processed += 1
                except Exception as e:
                    errors.append(f"Note {note.id}: {str(e)}")
                    logger.error(f"Failed to sync note {note.id}: {e}")
            
            if errors:
                logger.warning(f"Sync completed with {len(errors)} errors: {errors}")
            
            return {
                "processed": processed,
                "total": len(notes),
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Failed to sync notes: {e}")
            raise
    
    async def search_similar_notes(self, query: str, n_results: int = 5) -> List[Source]:
        """Search for notes similar to the query"""
        try:
            logger.info(f"Searching for query: '{query}' with n_results={n_results}")
            
            # Check collection count first
            count = self.collection.count()
            logger.info(f"Collection has {count} documents")
            
            # Generate query embedding
            query_embedding = self.embeddings_model.encode(query).tolist()
            logger.info(f"Generated embedding of length: {len(query_embedding)}")
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["metadatas", "documents", "distances"]
            )
            
            logger.info(f"ChromaDB query results structure: {list(results.keys())}")
            logger.info(f"Results IDs: {results.get('ids')}")
            logger.info(f"Results distances: {results.get('distances')}")
            
            sources = []
            
            if results['ids'] and results['ids'][0]:
                logger.info(f"Processing {len(results['ids'][0])} results")
                for i in range(len(results['ids'][0])):
                    metadata = results['metadatas'][0][i]
                    document = results['documents'][0][i]
                    distance = results['distances'][0][i]
                    
                    logger.info(f"Result {i}: distance={distance}, title={metadata.get('title', 'N/A')}")
                    
                    # Convert distance to similarity score (0-1, higher is better)
                    # ChromaDB distance can vary - let's handle different ranges
                    if distance <= 1.0:
                        # Standard case: cosine distance (0-2 range, where 0 is identical)
                        relevance_score = max(0, 1 - distance)
                    else:
                        # Distance > 1: convert to 0-1 range using inverse
                        relevance_score = 1 / (1 + distance)
                    
                    # Ensure minimum relevance for exact matches
                    if distance < 0.1:
                        relevance_score = max(relevance_score, 0.9)
                    
                    # Extract content snippet (first 200 chars)
                    content_snippet = document[:200] + "..." if len(document) > 200 else document
                    
                    source = Source(
                        note_id=metadata['note_id'],
                        title=metadata['title'],
                        content_snippet=content_snippet,
                        relevance_score=relevance_score,
                        created_at=datetime.fromisoformat(metadata['created_at']) if metadata.get('created_at') else None,
                        updated_at=datetime.fromisoformat(metadata['updated_at']) if metadata.get('updated_at') else None
                    )
                    
                    sources.append(source)
            else:
                logger.warning("No results returned from ChromaDB query")
            
            logger.info(f"Found {len(sources)} similar notes for query: {query[:50]}...")
            return sources
            
        except Exception as e:
            logger.error(f"Failed to search similar notes: {e}")
            raise
    
    async def delete_note(self, note_id: int):
        """Delete a note from the vector store"""
        try:
            doc_id = self._create_document_id(note_id)
            
            # Check if document exists
            existing = self.collection.get(ids=[doc_id])
            
            if existing['ids']:
                self.collection.delete(ids=[doc_id])
                logger.info(f"Deleted note {note_id} from vector store")
            else:
                logger.warning(f"Note {note_id} not found in vector store")
                
        except Exception as e:
            logger.error(f"Failed to delete note {note_id}: {e}")
            raise
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        try:
            count = self.collection.count()
            
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "embeddings_model": getattr(self.embeddings_model, 'model_name', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            raise
    
    async def clear_collection(self):
        """Clear all documents from the collection (for testing/reset)"""
        try:
            # Get all document IDs
            all_docs = self.collection.get()
            
            if all_docs['ids']:
                self.collection.delete(ids=all_docs['ids'])
                logger.info(f"Cleared {len(all_docs['ids'])} documents from collection")
            else:
                logger.info("Collection is already empty")
                
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            raise 