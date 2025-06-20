'use client';

import { ServiceHealth } from '@/lib';
import ModeSelector from './ModeSelector';

interface ChatHeaderProps {
  isHealthy: boolean;
  serviceHealth?: ServiceHealth | null;
  vectorStoreCount?: number;
  onSyncNotes?: () => void;
  onClearChat?: () => void;
  isSyncing?: boolean;
  selectedMode?: 'traditional' | 'agent';
  onModeChange?: (mode: 'traditional' | 'agent') => void;
}

export default function ChatHeader({ 
  isHealthy, 
  serviceHealth,
  vectorStoreCount = 0,
  onSyncNotes,
  onClearChat,
  isSyncing = false,
  selectedMode = 'traditional',
  onModeChange
}: ChatHeaderProps) {
  return (
    <div className="border-b border-gray-200 bg-white px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Title and status */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">AI Chat</h1>
              <p className="text-sm text-gray-500">Ask questions about your notes</p>
            </div>
          </div>

          {/* Status indicator */}
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className={`text-xs font-medium ${isHealthy ? 'text-green-700' : 'text-red-700'}`}>
              {isHealthy ? 'Online' : 'Offline'}
            </span>
          </div>
        </div>

        {/* Mode selector and actions */}
        <div className="flex items-center gap-4">
          {/* Mode selector */}
          {onModeChange && (
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-gray-600">Mode:</span>
              <ModeSelector
                selectedMode={selectedMode}
                onModeChange={onModeChange}
                disabled={!isHealthy || isSyncing}
              />
            </div>
          )}
          {/* Vector store info */}
          {isHealthy && (
            <div className="text-xs text-gray-600 bg-gray-50 px-3 py-2 rounded-lg">
              <div className="flex items-center gap-2">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                <span>{vectorStoreCount} notes indexed</span>
              </div>
            </div>
          )}

          {/* Sync button */}
          {onSyncNotes && (
            <button
              onClick={onSyncNotes}
              disabled={!isHealthy || isSyncing}
              className="flex items-center gap-2 px-3 py-2 text-xs font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              title="Sync all notes to AI"
            >
              {isSyncing ? (
                <>
                  <svg className="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Syncing...</span>
                </>
              ) : (
                <>
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>Sync Notes</span>
                </>
              )}
            </button>
          )}

          {/* Clear chat button */}
          {onClearChat && (
            <button
              onClick={onClearChat}
              className="flex items-center gap-2 px-3 py-2 text-xs font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors duration-200"
              title="Clear conversation"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              <span>Clear</span>
            </button>
          )}
        </div>
      </div>

      {/* Service health details (when offline) */}
      {!isHealthy && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start gap-2">
            <svg className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="text-sm">
              <p className="text-red-800 font-medium">AI Service Unavailable</p>
              <p className="text-red-700 mt-1">
                The AI chat service is currently offline. Please check that the LangChain service is running on port 8003.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 