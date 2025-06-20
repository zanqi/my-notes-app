'use client';

interface ModeSelectorProps {
  selectedMode: 'traditional' | 'agent';
  onModeChange: (mode: 'traditional' | 'agent') => void;
  disabled?: boolean;
}

export default function ModeSelector({ selectedMode, onModeChange, disabled = false }: ModeSelectorProps) {
  return (
    <div className="flex items-center gap-1 p-1 bg-gray-100 rounded-lg">
      <button
        onClick={() => onModeChange('traditional')}
        disabled={disabled}
        className={`
          px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-200
          ${selectedMode === 'traditional'
            ? 'bg-white text-gray-900 shadow-sm'
            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
        title="Traditional RAG - Fast and economical"
      >
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-blue-500"></div>
          <span>Traditional</span>
        </div>
      </button>
      
      <button
        onClick={() => onModeChange('agent')}
        disabled={disabled}
        className={`
          px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-200
          ${selectedMode === 'agent'
            ? 'bg-white text-gray-900 shadow-sm'
            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
        title="Agent RAG - Advanced with web search, hallucination detection, and quality checks"
      >
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-purple-500"></div>
          <span>Agent</span>
        </div>
      </button>
    </div>
  );
} 