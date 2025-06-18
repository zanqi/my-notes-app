'use client';

import { Source } from '@/lib';

interface SourceListProps {
  sources: Source[];
  maxVisible?: number;
}

export default function SourceList({ sources, maxVisible = 3 }: SourceListProps) {
  const visibleSources = sources.slice(0, maxVisible);
  const hasMore = sources.length > maxVisible;

  const getRelevanceColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-100 text-green-800 border-green-200';
    if (score >= 0.6) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const formatRelevanceScore = (score: number) => {
    return `${Math.round(score * 100)}%`;
  };

  if (sources.length === 0) return null;

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 text-xs text-gray-600">
        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>Based on {sources.length} note{sources.length !== 1 ? 's' : ''}:</span>
      </div>

      <div className="space-y-1.5">
        {visibleSources.map((source, index) => (
          <div
            key={`${source.note_id}-${index}`}
            className={`text-xs border rounded-md p-2 ${getRelevanceColor(source.relevance_score)}`}
          >
            <div className="flex items-start justify-between gap-2 mb-1">
              <h4 className="font-medium line-clamp-1 flex-1">
                {source.title || `Note #${source.note_id}`}
              </h4>
              <span className="text-xs opacity-75 whitespace-nowrap">
                {formatRelevanceScore(source.relevance_score)} match
              </span>
            </div>
            
            <p className="line-clamp-2 opacity-90 leading-relaxed">
              {source.content_snippet}
            </p>

            {source.created_at && (
              <div className="mt-1 text-xs opacity-75">
                {new Date(source.created_at).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })}
              </div>
            )}
          </div>
        ))}

        {hasMore && (
          <div className="text-xs text-gray-500 italic text-center py-1">
            +{sources.length - maxVisible} more source{sources.length - maxVisible !== 1 ? 's' : ''}
          </div>
        )}
      </div>
    </div>
  );
} 