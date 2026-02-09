import { useState, useCallback } from 'react';

/**
 * Hook for managing refresh control state
 */
export function useRefreshControl(onRefresh?: () => Promise<void>) {
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = useCallback(async () => {
    if (!onRefresh) return;

    setRefreshing(true);
    try {
      await onRefresh();
    } finally {
      setRefreshing(false);
    }
  }, [onRefresh]);

  return {
    refreshing,
    onRefresh: handleRefresh,
  };
}


