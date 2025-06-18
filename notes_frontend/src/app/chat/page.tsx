'use client';

import Link from 'next/link';
import { ChatContainer, Navigation } from '@/components';

export default function ChatPage() {
  const quickActions = (
    <Link
      href="/"
      className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-150"
    >
      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      View Notes
    </Link>
  );

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header with navigation */}
      <Navigation rightContent={quickActions} />

      {/* Chat container - takes full remaining height */}
      <div className="flex-1 flex">
        <div className="w-full max-w-7xl mx-auto">
          <ChatContainer className="h-full" />
        </div>
      </div>
    </div>
  );
} 