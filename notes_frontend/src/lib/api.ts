const API_BASE_URL = 'http://localhost:3001/api/v1';

export interface Note {
  id: number;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface CreateNoteData {
  title: string;
  content: string;
}

export interface UpdateNoteData {
  title?: string;
  content?: string;
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
      errorMessage = errorData.error || errorData.errors?.join(', ') || errorMessage;
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
    return handleResponse<Note>(response);
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
    return handleResponse<Note>(response);
  },

  // Delete a note
  async deleteNote(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/notes/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return handleResponse<void>(response);
  },
}; 