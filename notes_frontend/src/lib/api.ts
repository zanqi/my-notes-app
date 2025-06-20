const API_BASE_URL = 'http://localhost:3001/api/v1';
const LANGCHAIN_BASE_URL = 'http://localhost:8003';

export interface Note {
  id: number;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
  tags?: string[];
  category?: string;
}

export interface CreateNoteData {
  title: string;
  content: string;
  tags?: string[];
  category?: string;
}

export interface UpdateNoteData {
  title?: string;
  content?: string;
  tags?: string[];
  category?: string;
}

// Chat-related types
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: Source[];
}

export interface Source {
  note_id: number;
  title: string;
  content_snippet: string;
  relevance_score: number;
  created_at?: string;
  updated_at?: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  include_sources?: boolean;
  mode?: 'traditional' | 'agent';
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  sources: Source[];
  timestamp: string;
  tokens_used?: number;
}

export interface ConversationHistory {
  conversation_id: string;
  messages: ChatMessage[];
}

export interface ServiceHealth {
  status: string;
  services: {
    rag_service: string;
    vector_store: string;
  };
  collection_info: {
    collection_name: string;
    document_count: number;
    embeddings_model?: string;
  };
}

class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `HTTP error! status: ${response.status}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.error || errorData.errors?.join(', ') || errorData.detail || errorMessage;
    } catch {
      // If parsing JSON fails, use the default error message
    }
    throw new ApiError(errorMessage, response.status);
  }
  
  // Handle empty responses (like DELETE)
  if (response.status === 204) {
    return {} as T;
  }
  
  return response.json();
}

export const api = {
  // =====================================
  // NOTES API (Rails Backend)
  // =====================================
  
  // Get all notes
  async getNotes(): Promise<Note[]> {
    const response = await fetch(`${API_BASE_URL}/notes`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return handleResponse<Note[]>(response);
  },

  // Get a single note
  async getNote(id: number): Promise<Note> {
    const response = await fetch(`${API_BASE_URL}/notes/${id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return handleResponse<Note>(response);
  },

  // Create a new note
  async createNote(data: CreateNoteData): Promise<Note> {
    const response = await fetch(`${API_BASE_URL}/notes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ note: data }),
    });
    
    // After creating a note, sync it to the vector store
    const note = await handleResponse<Note>(response);
    try {
      await this.syncNoteToVectorStore(note);
    } catch (error) {
      console.warn('Failed to sync note to vector store:', error);
    }
    
    return note;
  },

  // Update a note
  async updateNote(id: number, data: UpdateNoteData): Promise<Note> {
    const response = await fetch(`${API_BASE_URL}/notes/${id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ note: data }),
    });
    
    // After updating a note, sync it to the vector store
    const note = await handleResponse<Note>(response);
    try {
      await this.syncNoteToVectorStore(note);
    } catch (error) {
      console.warn('Failed to sync updated note to vector store:', error);
    }
    
    return note;
  },

  // Delete a note
  async deleteNote(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/notes/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    // After deleting a note, remove it from the vector store
    try {
      await this.deleteNoteFromVectorStore(id);
    } catch (error) {
      console.warn('Failed to remove note from vector store:', error);
    }
    
    return handleResponse<void>(response);
  },

  // =====================================
  // LANGCHAIN AI CHAT API
  // =====================================

  // Send a chat message
  async sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${LANGCHAIN_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    return handleResponse<ChatResponse>(response);
  },

  // Get conversation history
  async getConversationHistory(conversationId: string): Promise<ConversationHistory> {
    const response = await fetch(`${LANGCHAIN_BASE_URL}/conversations/${conversationId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return handleResponse<ConversationHistory>(response);
  },

  // Check LangChain service health
  async checkChatHealth(): Promise<ServiceHealth> {
    const response = await fetch(`${LANGCHAIN_BASE_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return handleResponse<ServiceHealth>(response);
  },

  // =====================================
  // VECTOR STORE SYNC OPERATIONS
  // =====================================

  // Sync a single note to the vector store
  async syncNoteToVectorStore(note: Note): Promise<void> {
    const response = await fetch(`${LANGCHAIN_BASE_URL}/add_note`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        id: note.id,
        title: note.title,
        content: note.content,
        created_at: note.created_at,
        updated_at: note.updated_at,
        tags: note.tags || [],
        category: note.category || null,
      }),
    });
    return handleResponse<void>(response);
  },

  // Remove a note from the vector store
  async deleteNoteFromVectorStore(noteId: number): Promise<void> {
    const response = await fetch(`${LANGCHAIN_BASE_URL}/notes/${noteId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return handleResponse<void>(response);
  },

  // Sync all notes to the vector store
  async syncAllNotesToVectorStore(): Promise<{ processed: number; total: number }> {
    try {
      // Get all notes from Rails API
      const notes = await this.getNotes();
      
      // Transform to the format expected by LangChain service
      const formattedNotes = notes.map(note => ({
        id: note.id,
        title: note.title,
        content: note.content,
        created_at: note.created_at,
        updated_at: note.updated_at,
        tags: note.tags || [],
        category: note.category || null,
      }));

      // Send to LangChain service
      const response = await fetch(`${LANGCHAIN_BASE_URL}/sync_notes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ notes: formattedNotes }),
      });
      
      return handleResponse<{ processed: number; total: number }>(response);
    } catch (error) {
      console.error('Failed to sync notes to vector store:', error);
      throw error;
    }
  },

  // =====================================
  // UTILITY METHODS
  // =====================================

  // Test connection to both services
  async testConnections(): Promise<{ rails: boolean; langchain: boolean }> {
    const results = { rails: false, langchain: false };
    
    try {
      await this.getNotes();
      results.rails = true;
    } catch (error) {
      console.warn('Rails API connection failed:', error);
    }
    
    try {
      await this.checkChatHealth();
      results.langchain = true;
    } catch (error) {
      console.warn('LangChain service connection failed:', error);
    }
    
    return results;
  },
}; 