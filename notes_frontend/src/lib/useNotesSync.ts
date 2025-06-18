'use client';

import { useState, useCallback, useEffect } from 'react';
import { api, Note, ServiceHealth } from './api';

export interface UseNotesSyncOptions {
  autoSync?: boolean;
  onSyncComplete?: (result: { processed: number; total: number }) => void;
  onSyncError?: (error: Error) => void;
}

export interface UseNotesSyncReturn {
  isSyncing: boolean;
  syncError: string | null;
  lastSyncTime: Date | null;
  vectorStoreCount: number;
  serviceHealth: ServiceHealth | null;
  syncAllNotes: () => Promise<void>;
  syncSingleNote: (note: Note) => Promise<void>;
  checkServiceHealth: () => Promise<void>;
  clearSyncError: () => void;
}

export function useNotesSync(options: UseNotesSyncOptions = {}): UseNotesSyncReturn {
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncError, setSyncError] = useState<string | null>(null);
  const [lastSyncTime, setLastSyncTime] = useState<Date | null>(null);
  const [vectorStoreCount, setVectorStoreCount] = useState(0);
  const [serviceHealth, setServiceHealth] = useState<ServiceHealth | null>(null);

  // Check service health on mount and periodically
  useEffect(() => {
    checkServiceHealth();
    
    // Check health every 30 seconds
    const interval = setInterval(checkServiceHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkServiceHealth = useCallback(async () => {
    try {
      const health = await api.checkChatHealth();
      setServiceHealth(health);
      setVectorStoreCount(health.collection_info.document_count);
    } catch (err) {
      console.warn('Failed to check service health:', err);
      setServiceHealth(null);
    }
  }, []);

  const syncAllNotes = useCallback(async () => {
    if (isSyncing) return;
    
    setIsSyncing(true);
    setSyncError(null);

    try {
      const result = await api.syncAllNotesToVectorStore();
      setLastSyncTime(new Date());
      setVectorStoreCount(result.processed);
      
      // Call success callback if provided
      options.onSyncComplete?.(result);
      
      // Refresh service health to get updated count
      await checkServiceHealth();
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to sync notes';
      setSyncError(errorMessage);
      
      // Call error callback if provided
      options.onSyncError?.(err instanceof Error ? err : new Error(errorMessage));
    } finally {
      setIsSyncing(false);
    }
  }, [isSyncing, options, checkServiceHealth]);

  const syncSingleNote = useCallback(async (note: Note) => {
    try {
      await api.syncNoteToVectorStore(note);
      
      // Refresh service health to get updated count
      await checkServiceHealth();
      
    } catch (err) {
      console.warn('Failed to sync single note:', err);
      // Don't set sync error for single note failures as they're often background operations
    }
  }, [checkServiceHealth]);

  const clearSyncError = useCallback(() => {
    setSyncError(null);
  }, []);

  // Auto-sync functionality
  useEffect(() => {
    if (options.autoSync && serviceHealth?.status === 'healthy' && vectorStoreCount === 0) {
      // If auto-sync is enabled, the service is healthy, and there are no notes in the vector store,
      // automatically sync all notes
      const timeoutId = setTimeout(() => {
        syncAllNotes();
      }, 2000); // Wait 2 seconds to avoid immediate sync on load
      
      return () => clearTimeout(timeoutId);
    }
  }, [options.autoSync, serviceHealth, vectorStoreCount, syncAllNotes]);

  return {
    isSyncing,
    syncError,
    lastSyncTime,
    vectorStoreCount,
    serviceHealth,
    syncAllNotes,
    syncSingleNote,
    checkServiceHealth,
    clearSyncError,
  };
} 