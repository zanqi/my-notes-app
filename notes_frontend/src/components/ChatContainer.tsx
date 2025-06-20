'use client';

import { useEffect, useRef, useState } from 'react';
import { useChat, useNotesSync } from '@/lib';
import ChatHeader from './ChatHeader';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

interface ChatContainerProps {
  className?: string;
}

export default function ChatContainer({ className = '' }: ChatContainerProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [selectedMode, setSelectedMode] = useState<'traditional' | 'agent'>('traditional');
  
  // Chat functionality
  const { 
    messages, 
    isLoading, 
    error,
    sendMessage, 
    clearConversation,
    isHealthy,
  } = useChat({
    includeSources: true,
    mode: selectedMode,
    onError: (error) => {
      console.error('Chat error:', error);
    },
  });

  // Notes sync functionality
  const {
    isSyncing,
    syncError,
    vectorStoreCount,
    serviceHealth,
    syncAllNotes,
    clearSyncError,
  } = useNotesSync({
    autoSync: true,
    onSyncComplete: (result) => {
      console.log(`Synced ${result.processed}/${result.total} notes`);
    },
    onSyncError: (error) => {
      console.error('Sync error:', error);
    },
  });

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleClearChat = () => {
    if (confirm('Clear this conversation? This action cannot be undone.')) {
      clearConversation();
    }
  };

  const hasMessages = messages.length > 0;
  const showError = error || syncError;

  return (
    <div className={`flex flex-col h-full bg-gray-50 ${className}`}>
      {/* Header */}
      <ChatHeader
        isHealthy={isHealthy}
        serviceHealth={serviceHealth}
        vectorStoreCount={vectorStoreCount}
        onSyncNotes={syncAllNotes}
        onClearChat={hasMessages ? handleClearChat : undefined}
        isSyncing={isSyncing}
        selectedMode={selectedMode}
        onModeChange={setSelectedMode}
      />

      {/* Error banner */}
      {showError && (
        <div className="mx-6 mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-start gap-2">
              <svg className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="text-sm">
                <p className="text-red-800 font-medium">
                  {error ? 'Chat Error' : 'Sync Error'}
                </p>
                <p className="text-red-700 mt-1">
                  {error || syncError}
                </p>
              </div>
            </div>
            <button
              onClick={() => {
                if (syncError) clearSyncError();
                // Chat errors clear automatically on next successful message
              }}
              className="text-red-500 hover:text-red-700"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto">
        {hasMessages ? (
          <div className="p-6 space-y-4">
            {messages.map((message, index) => (
              <ChatMessage
                key={`${message.timestamp}-${index}`}
                message={message}
                isLatest={index === messages.length - 1}
              />
            ))}
            
            {/* Loading indicator */}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="flex items-center gap-2 bg-gray-100 text-gray-700 rounded-lg px-4 py-3 max-w-[80%]">
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span className="text-sm">AI is thinking...</span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center p-6">
            <div className="text-center max-w-md">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Welcome to AI Chat
              </h3>
              
              <p className="text-gray-600 mb-6">
                Ask questions about your notes and I'll help you find relevant information using AI-powered search.
              </p>

              {isHealthy ? (
                <div className="space-y-2 text-sm text-gray-500">
                  <p>💡 Try asking:</p>
                  <ul className="space-y-1">
                    <li>"What notes do I have about work?"</li>
                    <li>"Summarize my recent thoughts"</li>
                    <li>"Find notes related to projects"</li>
                  </ul>
                  
                  {vectorStoreCount > 0 && (
                    <p className="mt-4 text-green-600">
                      ✅ {vectorStoreCount} notes are ready for AI search
                    </p>
                  )}
                  
                  {vectorStoreCount === 0 && (
                    <p className="mt-4 text-yellow-600">
                      ⚠️ No notes indexed yet. Click "Sync Notes" to get started.
                    </p>
                  )}
                </div>
              ) : (
                <p className="text-red-600 text-sm">
                  🔴 AI service is offline. Please start the LangChain service.
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Input area */}
      <ChatInput
        onSend={sendMessage}
        disabled={!isHealthy || isLoading}
        placeholder={
          !isHealthy 
            ? "AI service offline..." 
            : vectorStoreCount === 0
            ? "Sync your notes first, then ask questions..."
            : "Ask about your notes..."
        }
      />
    </div>
  );
} 