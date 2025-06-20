'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { api, ChatMessage, ChatResponse, Source } from './api';

export interface UseChatOptions {
  conversationId?: string;
  includeSources?: boolean;
  mode?: 'traditional' | 'agent';
  onError?: (error: Error) => void;
  onResponse?: (response: ChatResponse) => void;
}

export interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  conversationId: string | null;
  sendMessage: (message: string) => Promise<void>;
  clearConversation: () => void;
  retryLastMessage: () => Promise<void>;
  isHealthy: boolean;
  checkHealth: () => Promise<void>;
}

export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(options.conversationId || null);
  const [isHealthy, setIsHealthy] = useState(false);
  const lastMessageRef = useRef<string>('');

  // Check service health on mount
  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = useCallback(async () => {
    try {
      await api.checkChatHealth();
      setIsHealthy(true);
    } catch (err) {
      setIsHealthy(false);
      console.warn('Chat service health check failed:', err);
    }
  }, []);

  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim()) return;
    
    setIsLoading(true);
    setError(null);
    lastMessageRef.current = message;

    // Add user message immediately
    const userMessage: ChatMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await api.sendChatMessage({
        message,
        conversation_id: conversationId || undefined,
        include_sources: options.includeSources ?? true,
        mode: options.mode || 'traditional',
      });

      // Update conversation ID if it's new
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
        sources: response.sources,
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Call onResponse callback if provided
      options.onResponse?.(response);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      
      // Remove the user message on error
      setMessages(prev => prev.slice(0, -1));
      
      // Call onError callback if provided
      options.onError?.(err instanceof Error ? err : new Error(errorMessage));
    } finally {
      setIsLoading(false);
    }
  }, [conversationId, options]);

  const retryLastMessage = useCallback(async () => {
    if (lastMessageRef.current) {
      await sendMessage(lastMessageRef.current);
    }
  }, [sendMessage]);

  const clearConversation = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    lastMessageRef.current = '';
  }, []);

  return {
    messages,
    isLoading,
    error,
    conversationId,
    sendMessage,
    clearConversation,
    retryLastMessage,
    isHealthy,
    checkHealth,
  };
} 