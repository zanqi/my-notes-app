'use client';

import { useState, useRef, useEffect } from 'react';

interface ChatInputProps {
  onSend: (message: string) => Promise<void>;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
  selectedMode?: 'traditional' | 'agent';
  onModeChange?: (mode: 'traditional' | 'agent') => void;
}

export default function ChatInput({ 
  onSend, 
  disabled = false, 
  placeholder = "Ask about your notes...",
  maxLength = 1000,
  selectedMode = 'traditional',
  onModeChange
}: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const trimmedMessage = message.trim();
    if (!trimmedMessage || disabled || isSending) return;

    setIsSending(true);
    
    try {
      await onSend(trimmedMessage);
      setMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
      // Keep the message in the input on error so user can retry
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  const handleModeSelect = (mode: 'traditional' | 'agent') => {
    onModeChange?.(mode);
    setIsDropdownOpen(false);
  };

  const isDisabled = disabled || isSending;
  const remainingChars = maxLength - message.length;
  const isNearLimit = remainingChars <= 50;

  const getModeLabel = (mode: 'traditional' | 'agent') => {
    return mode === 'traditional' ? 'Traditional' : 'Agent';
  };

  const getModeColor = (mode: 'traditional' | 'agent') => {
    return mode === 'traditional' ? 'bg-blue-500' : 'bg-purple-500';
  };

  const getModeDescription = (mode: 'traditional' | 'agent') => {
    return mode === 'traditional' 
      ? 'Fast and economical' 
      : 'Advanced with web search and quality checks';
  };

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <form onSubmit={handleSubmit} className="space-y-2">
        {/* Mode selector dropdown - positioned above textarea */}
        {onModeChange && (
          <div className="flex items-center justify-between mb-2">
            <div className="relative" ref={dropdownRef}>
              <button
                type="button"
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                disabled={isDisabled}
                className={`flex items-center gap-1.5 px-2 py-1 text-xs font-medium rounded-md transition-all duration-200 border ${
                  isDisabled 
                    ? 'opacity-50 cursor-not-allowed border-gray-200 bg-gray-50' 
                    : 'hover:bg-gray-50 cursor-pointer border-gray-200 bg-white shadow-sm'
                } text-gray-700`}
                title={`Current mode: ${getModeLabel(selectedMode)} - ${getModeDescription(selectedMode)}`}
              >
                <div className={`w-2 h-2 rounded-full ${getModeColor(selectedMode)}`}></div>
                <span>{getModeLabel(selectedMode)}</span>
                <svg
                  className={`w-3 h-3 transition-transform duration-200 ${
                    isDropdownOpen ? 'rotate-180' : 'rotate-0'
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* Dropdown menu */}
              {isDropdownOpen && (
                <div className="absolute top-full left-0 mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-20">
                  <button
                    type="button"
                    onClick={() => handleModeSelect('traditional')}
                    className={`w-full px-3 py-2 text-left text-xs font-medium transition-all duration-200 rounded-t-lg ${
                      selectedMode === 'traditional'
                        ? 'bg-blue-50 text-blue-900'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                        <span>Traditional</span>
                      </div>
                      {selectedMode === 'traditional' && (
                        <svg className="w-3 h-3 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </div>
                    <p className="text-gray-500 mt-1 text-xs">Fast and economical</p>
                  </button>
                  
                  <button
                    type="button"
                    onClick={() => handleModeSelect('agent')}
                    className={`w-full px-3 py-2 text-left text-xs font-medium transition-all duration-200 rounded-b-lg ${
                      selectedMode === 'agent'
                        ? 'bg-purple-50 text-purple-900'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-purple-500"></div>
                        <span>Agent</span>
                      </div>
                      {selectedMode === 'agent' && (
                        <svg className="w-3 h-3 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </div>
                    <p className="text-gray-500 mt-1 text-xs">Advanced with web search and quality checks</p>
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={isDisabled}
            maxLength={maxLength}
            rows={1}
            className={`w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all duration-200 ${
              isDisabled ? 'bg-gray-50 cursor-not-allowed' : ''
            } ${message.length > 0 ? 'min-h-[44px]' : ''}`}
            style={{ maxHeight: '120px' }}
          />
          
          {/* Send button */}
          <button
            type="submit"
            disabled={isDisabled || !message.trim()}
            className={`absolute right-2 bottom-2 w-8 h-8 rounded-full flex items-center justify-center transition-all duration-200 ${
              message.trim() && !isDisabled
                ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            }`}
            title="Send message (Enter)"
          >
            {isSending ? (
              <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>

        {/* Character count and tips */}
        <div className="flex justify-between items-center text-xs text-gray-500">
          <div className="flex items-center gap-4">
            <span>Press Enter to send, Shift+Enter for new line</span>
          </div>
          
          {isNearLimit && (
            <span className={remainingChars < 0 ? 'text-red-500' : 'text-yellow-600'}>
              {remainingChars} characters remaining
            </span>
          )}
        </div>
      </form>
    </div>
  );
} 