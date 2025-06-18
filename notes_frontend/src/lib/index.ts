// API Client and Types
export { api } from './api';
export type {
  Note,
  CreateNoteData,
  UpdateNoteData,
  ChatMessage,
  Source,
  ChatRequest,
  ChatResponse,
  ConversationHistory,
  ServiceHealth,
} from './api';

// Chat Hook
export { useChat } from './useChat';
export type { UseChatOptions, UseChatReturn } from './useChat';

// Notes Sync Hook
export { useNotesSync } from './useNotesSync';
export type { UseNotesSyncOptions, UseNotesSyncReturn } from './useNotesSync'; 