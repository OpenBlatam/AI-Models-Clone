import { useState, useEffect, useCallback } from 'react';
import { offlineManager, SyncStatus } from '../../lib/offline/offline-manager';
import { dataSyncManager, SyncResult } from '../../lib/offline/data-sync';

export interface UseOfflineSyncReturn {
  // Network state
  isOnline: boolean;
  isConnected: boolean;
  
  // Sync status
  syncStatus: SyncStatus;
  isSyncing: boolean;
  lastSync: number | null;
  pendingActions: number;
  failedActions: number;
  syncProgress: number;
  
  // Data sync
  hasConflicts: boolean;
  conflicts: any[];
  localDataCount: number;
  
  // Actions
  sync: () => Promise<SyncResult>;
  forceSync: () => Promise<void>;
  clearPendingActions: () => Promise<void>;
  resolveConflict: (id: string, resolution: 'server' | 'client' | 'merge', mergedData?: any) => Promise<boolean>;
  
  // Data operations
  createData: (type: string, data: any) => Promise<string>;
  updateData: (id: string, data: any) => Promise<boolean>;
  deleteData: (id: string) => Promise<boolean>;
  getData: (id: string) => any;
  getAllData: (type?: string) => any[];
  
  // Queue operations
  queueAction: (type: string, payload: any, priority?: number) => Promise<string>;
  removeAction: (actionId: string) => Promise<boolean>;
  getPendingActions: () => any[];
}

export function useOfflineSync(): UseOfflineSyncReturn {
  const [isOnline, setIsOnline] = useState(offlineManager.isConnected);
  const [syncStatus, setSyncStatus] = useState<SyncStatus>(offlineManager.status);
  const [hasConflicts, setHasConflicts] = useState(dataSyncManager.hasConflicts);
  const [conflicts, setConflicts] = useState(dataSyncManager.getConflicts());
  const [localDataCount, setLocalDataCount] = useState(dataSyncManager.localDataCount);

  // Update state when offline manager events occur
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
    };

    const handleOffline = () => {
      setIsOnline(false);
    };

    const handleSyncStarted = () => {
      setSyncStatus(prev => ({ ...prev, isSyncing: true }));
    };

    const handleSyncCompleted = () => {
      setSyncStatus(prev => ({ ...prev, isSyncing: false, lastSync: Date.now() }));
    };

    const handleSyncFailed = (error: any) => {
      setSyncStatus(prev => ({ ...prev, isSyncing: false }));
      console.error('Sync failed:', error);
    };

    const handleSyncProgress = (progress: number) => {
      setSyncStatus(prev => ({ ...prev, syncProgress: progress }));
    };

    const handleActionQueued = () => {
      setSyncStatus(offlineManager.status);
    };

    const handleActionCompleted = () => {
      setSyncStatus(offlineManager.status);
    };

    const handleActionFailed = () => {
      setSyncStatus(offlineManager.status);
    };

    const handleNetworkStateChange = (state: any) => {
      setIsOnline(state.isConnected);
    };

    // Data sync manager events
    const handleDataCreated = () => {
      setLocalDataCount(dataSyncManager.localDataCount);
    };

    const handleDataUpdated = () => {
      setLocalDataCount(dataSyncManager.localDataCount);
    };

    const handleDataDeleted = () => {
      setLocalDataCount(dataSyncManager.localDataCount);
    };

    const handleConflictResolved = () => {
      setHasConflicts(dataSyncManager.hasConflicts);
      setConflicts(dataSyncManager.getConflicts());
    };

    const handleSyncCompletedData = () => {
      setHasConflicts(dataSyncManager.hasConflicts);
      setConflicts(dataSyncManager.getConflicts());
      setLocalDataCount(dataSyncManager.localDataCount);
    };

    // Subscribe to events
    offlineManager.on('online', handleOnline);
    offlineManager.on('offline', handleOffline);
    offlineManager.on('syncStarted', handleSyncStarted);
    offlineManager.on('syncCompleted', handleSyncCompleted);
    offlineManager.on('syncFailed', handleSyncFailed);
    offlineManager.on('syncProgress', handleSyncProgress);
    offlineManager.on('actionQueued', handleActionQueued);
    offlineManager.on('actionCompleted', handleActionCompleted);
    offlineManager.on('actionFailed', handleActionFailed);
    offlineManager.on('networkStateChange', handleNetworkStateChange);

    dataSyncManager.on('dataCreated', handleDataCreated);
    dataSyncManager.on('dataUpdated', handleDataUpdated);
    dataSyncManager.on('dataDeleted', handleDataDeleted);
    dataSyncManager.on('conflictResolved', handleConflictResolved);
    dataSyncManager.on('syncCompleted', handleSyncCompletedData);

    // Cleanup
    return () => {
      offlineManager.off('online', handleOnline);
      offlineManager.off('offline', handleOffline);
      offlineManager.off('syncStarted', handleSyncStarted);
      offlineManager.off('syncCompleted', handleSyncCompleted);
      offlineManager.off('syncFailed', handleSyncFailed);
      offlineManager.off('syncProgress', handleSyncProgress);
      offlineManager.off('actionQueued', handleActionQueued);
      offlineManager.off('actionCompleted', handleActionCompleted);
      offlineManager.off('actionFailed', handleActionFailed);
      offlineManager.off('networkStateChange', handleNetworkStateChange);

      dataSyncManager.off('dataCreated', handleDataCreated);
      dataSyncManager.off('dataUpdated', handleDataUpdated);
      dataSyncManager.off('dataDeleted', handleDataDeleted);
      dataSyncManager.off('conflictResolved', handleConflictResolved);
      dataSyncManager.off('syncCompleted', handleSyncCompletedData);
    };
  }, []);

  // Sync with server
  const sync = useCallback(async (): Promise<SyncResult> => {
    return await dataSyncManager.syncWithServer();
  }, []);

  // Force sync
  const forceSync = useCallback(async (): Promise<void> => {
    await offlineManager.forceSync();
  }, []);

  // Clear pending actions
  const clearPendingActions = useCallback(async (): Promise<void> => {
    await offlineManager.clearPendingActions();
    setSyncStatus(offlineManager.status);
  }, []);

  // Resolve conflict
  const resolveConflict = useCallback(async (
    id: string, 
    resolution: 'server' | 'client' | 'merge', 
    mergedData?: any
  ): Promise<boolean> => {
    const result = await dataSyncManager.resolveConflict(id, resolution, mergedData);
    if (result) {
      setHasConflicts(dataSyncManager.hasConflicts);
      setConflicts(dataSyncManager.getConflicts());
    }
    return result;
  }, []);

  // Data operations
  const createData = useCallback(async (type: string, data: any): Promise<string> => {
    return await dataSyncManager.create(type, data);
  }, []);

  const updateData = useCallback(async (id: string, data: any): Promise<boolean> => {
    return await dataSyncManager.update(id, data);
  }, []);

  const deleteData = useCallback(async (id: string): Promise<boolean> => {
    return await dataSyncManager.delete(id);
  }, []);

  const getData = useCallback((id: string): any => {
    return dataSyncManager.get(id);
  }, []);

  const getAllData = useCallback((type?: string): any[] => {
    return dataSyncManager.getAll(type);
  }, []);

  // Queue operations
  const queueAction = useCallback(async (
    type: string, 
    payload: any, 
    priority: number = 0
  ): Promise<string> => {
    const actionId = await offlineManager.queueAction(type, payload, priority);
    setSyncStatus(offlineManager.status);
    return actionId;
  }, []);

  const removeAction = useCallback(async (actionId: string): Promise<boolean> => {
    const result = await offlineManager.removeAction(actionId);
    if (result) {
      setSyncStatus(offlineManager.status);
    }
    return result;
  }, []);

  const getPendingActions = useCallback((): any[] => {
    return offlineManager.getPendingActions();
  }, []);

  return {
    // Network state
    isOnline,
    isConnected: isOnline,
    
    // Sync status
    syncStatus,
    isSyncing: syncStatus.isSyncing,
    lastSync: syncStatus.lastSync,
    pendingActions: syncStatus.pendingActions,
    failedActions: syncStatus.failedActions,
    syncProgress: syncStatus.syncProgress,
    
    // Data sync
    hasConflicts,
    conflicts,
    localDataCount,
    
    // Actions
    sync,
    forceSync,
    clearPendingActions,
    resolveConflict,
    
    // Data operations
    createData,
    updateData,
    deleteData,
    getData,
    getAllData,
    
    // Queue operations
    queueAction,
    removeAction,
    getPendingActions,
  };
}
import { offlineManager, SyncStatus } from '../../lib/offline/offline-manager';
import { dataSyncManager, SyncResult } from '../../lib/offline/data-sync';

export interface UseOfflineSyncReturn {
  // Network state
  isOnline: boolean;
  isConnected: boolean;
  
  // Sync status
  syncStatus: SyncStatus;
  isSyncing: boolean;
  lastSync: number | null;
  pendingActions: number;
  failedActions: number;
  syncProgress: number;
  
  // Data sync
  hasConflicts: boolean;
  conflicts: any[];
  localDataCount: number;
  
  // Actions
  sync: () => Promise<SyncResult>;
  forceSync: () => Promise<void>;
  clearPendingActions: () => Promise<void>;
  resolveConflict: (id: string, resolution: 'server' | 'client' | 'merge', mergedData?: any) => Promise<boolean>;
  
  // Data operations
  createData: (type: string, data: any) => Promise<string>;
  updateData: (id: string, data: any) => Promise<boolean>;
  deleteData: (id: string) => Promise<boolean>;
  getData: (id: string) => any;
  getAllData: (type?: string) => any[];
  
  // Queue operations
  queueAction: (type: string, payload: any, priority?: number) => Promise<string>;
  removeAction: (actionId: string) => Promise<boolean>;
  getPendingActions: () => any[];
}

export function useOfflineSync(): UseOfflineSyncReturn {
  const [isOnline, setIsOnline] = useState(offlineManager.isConnected);
  const [syncStatus, setSyncStatus] = useState<SyncStatus>(offlineManager.status);
  const [hasConflicts, setHasConflicts] = useState(dataSyncManager.hasConflicts);
  const [conflicts, setConflicts] = useState(dataSyncManager.getConflicts());
  const [localDataCount, setLocalDataCount] = useState(dataSyncManager.localDataCount);

  // Update state when offline manager events occur
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
    };

    const handleOffline = () => {
      setIsOnline(false);
    };

    const handleSyncStarted = () => {
      setSyncStatus(prev => ({ ...prev, isSyncing: true }));
    };

    const handleSyncCompleted = () => {
      setSyncStatus(prev => ({ ...prev, isSyncing: false, lastSync: Date.now() }));
    };

    const handleSyncFailed = (error: any) => {
      setSyncStatus(prev => ({ ...prev, isSyncing: false }));
      console.error('Sync failed:', error);
    };

    const handleSyncProgress = (progress: number) => {
      setSyncStatus(prev => ({ ...prev, syncProgress: progress }));
    };

    const handleActionQueued = () => {
      setSyncStatus(offlineManager.status);
    };

    const handleActionCompleted = () => {
      setSyncStatus(offlineManager.status);
    };

    const handleActionFailed = () => {
      setSyncStatus(offlineManager.status);
    };

    const handleNetworkStateChange = (state: any) => {
      setIsOnline(state.isConnected);
    };

    // Data sync manager events
    const handleDataCreated = () => {
      setLocalDataCount(dataSyncManager.localDataCount);
    };

    const handleDataUpdated = () => {
      setLocalDataCount(dataSyncManager.localDataCount);
    };

    const handleDataDeleted = () => {
      setLocalDataCount(dataSyncManager.localDataCount);
    };

    const handleConflictResolved = () => {
      setHasConflicts(dataSyncManager.hasConflicts);
      setConflicts(dataSyncManager.getConflicts());
    };

    const handleSyncCompletedData = () => {
      setHasConflicts(dataSyncManager.hasConflicts);
      setConflicts(dataSyncManager.getConflicts());
      setLocalDataCount(dataSyncManager.localDataCount);
    };

    // Subscribe to events
    offlineManager.on('online', handleOnline);
    offlineManager.on('offline', handleOffline);
    offlineManager.on('syncStarted', handleSyncStarted);
    offlineManager.on('syncCompleted', handleSyncCompleted);
    offlineManager.on('syncFailed', handleSyncFailed);
    offlineManager.on('syncProgress', handleSyncProgress);
    offlineManager.on('actionQueued', handleActionQueued);
    offlineManager.on('actionCompleted', handleActionCompleted);
    offlineManager.on('actionFailed', handleActionFailed);
    offlineManager.on('networkStateChange', handleNetworkStateChange);

    dataSyncManager.on('dataCreated', handleDataCreated);
    dataSyncManager.on('dataUpdated', handleDataUpdated);
    dataSyncManager.on('dataDeleted', handleDataDeleted);
    dataSyncManager.on('conflictResolved', handleConflictResolved);
    dataSyncManager.on('syncCompleted', handleSyncCompletedData);

    // Cleanup
    return () => {
      offlineManager.off('online', handleOnline);
      offlineManager.off('offline', handleOffline);
      offlineManager.off('syncStarted', handleSyncStarted);
      offlineManager.off('syncCompleted', handleSyncCompleted);
      offlineManager.off('syncFailed', handleSyncFailed);
      offlineManager.off('syncProgress', handleSyncProgress);
      offlineManager.off('actionQueued', handleActionQueued);
      offlineManager.off('actionCompleted', handleActionCompleted);
      offlineManager.off('actionFailed', handleActionFailed);
      offlineManager.off('networkStateChange', handleNetworkStateChange);

      dataSyncManager.off('dataCreated', handleDataCreated);
      dataSyncManager.off('dataUpdated', handleDataUpdated);
      dataSyncManager.off('dataDeleted', handleDataDeleted);
      dataSyncManager.off('conflictResolved', handleConflictResolved);
      dataSyncManager.off('syncCompleted', handleSyncCompletedData);
    };
  }, []);

  // Sync with server
  const sync = useCallback(async (): Promise<SyncResult> => {
    return await dataSyncManager.syncWithServer();
  }, []);

  // Force sync
  const forceSync = useCallback(async (): Promise<void> => {
    await offlineManager.forceSync();
  }, []);

  // Clear pending actions
  const clearPendingActions = useCallback(async (): Promise<void> => {
    await offlineManager.clearPendingActions();
    setSyncStatus(offlineManager.status);
  }, []);

  // Resolve conflict
  const resolveConflict = useCallback(async (
    id: string, 
    resolution: 'server' | 'client' | 'merge', 
    mergedData?: any
  ): Promise<boolean> => {
    const result = await dataSyncManager.resolveConflict(id, resolution, mergedData);
    if (result) {
      setHasConflicts(dataSyncManager.hasConflicts);
      setConflicts(dataSyncManager.getConflicts());
    }
    return result;
  }, []);

  // Data operations
  const createData = useCallback(async (type: string, data: any): Promise<string> => {
    return await dataSyncManager.create(type, data);
  }, []);

  const updateData = useCallback(async (id: string, data: any): Promise<boolean> => {
    return await dataSyncManager.update(id, data);
  }, []);

  const deleteData = useCallback(async (id: string): Promise<boolean> => {
    return await dataSyncManager.delete(id);
  }, []);

  const getData = useCallback((id: string): any => {
    return dataSyncManager.get(id);
  }, []);

  const getAllData = useCallback((type?: string): any[] => {
    return dataSyncManager.getAll(type);
  }, []);

  // Queue operations
  const queueAction = useCallback(async (
    type: string, 
    payload: any, 
    priority: number = 0
  ): Promise<string> => {
    const actionId = await offlineManager.queueAction(type, payload, priority);
    setSyncStatus(offlineManager.status);
    return actionId;
  }, []);

  const removeAction = useCallback(async (actionId: string): Promise<boolean> => {
    const result = await offlineManager.removeAction(actionId);
    if (result) {
      setSyncStatus(offlineManager.status);
    }
    return result;
  }, []);

  const getPendingActions = useCallback((): any[] => {
    return offlineManager.getPendingActions();
  }, []);

  return {
    // Network state
    isOnline,
    isConnected: isOnline,
    
    // Sync status
    syncStatus,
    isSyncing: syncStatus.isSyncing,
    lastSync: syncStatus.lastSync,
    pendingActions: syncStatus.pendingActions,
    failedActions: syncStatus.failedActions,
    syncProgress: syncStatus.syncProgress,
    
    // Data sync
    hasConflicts,
    conflicts,
    localDataCount,
    
    // Actions
    sync,
    forceSync,
    clearPendingActions,
    resolveConflict,
    
    // Data operations
    createData,
    updateData,
    deleteData,
    getData,
    getAllData,
    
    // Queue operations
    queueAction,
    removeAction,
    getPendingActions,
  };
}


