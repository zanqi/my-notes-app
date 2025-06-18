'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface NavigationProps {
  rightContent?: React.ReactNode;
}

export default function Navigation({ rightContent }: NavigationProps) {
  const pathname = usePathname();

  const navItems = [
    { href: '/', label: 'Notes', icon: 'notes' },
    { href: '/chat', label: 'AI Chat', icon: 'chat' },
  ];

  const getIcon = (iconType: string) => {
    switch (iconType) {
      case 'notes':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        );
      case 'chat':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          <div className="flex items-center gap-6">
            <h1 className="text-3xl font-bold text-gray-900">Personal Notes</h1>
            
            {/* Navigation */}
            <nav className="flex space-x-1">
              {navItems.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`inline-flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-md transition-colors duration-150 ${
                      isActive
                        ? 'text-blue-600 bg-blue-50'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    {getIcon(item.icon)}
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Right content */}
          {rightContent && (
            <div className="flex items-center gap-3">
              {rightContent}
            </div>
          )}
        </div>
      </div>
    </header>
  );
} 