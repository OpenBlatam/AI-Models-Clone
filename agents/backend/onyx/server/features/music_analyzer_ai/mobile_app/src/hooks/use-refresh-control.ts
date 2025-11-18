import { useCallback, useState } from 'react';
import { RefreshControl } from 'react-native';
import { COLORS } from '../constants/config';

interface UseRefreshControlOptions {
  onRefresh: () => Promise<void> | void;
  refreshing?: boolean;
  tintColor?: string;
  colors?: string[];
}

/**
 * Hook for pull-to-refresh functionality
 * Provides RefreshControl component and state management
 */
export function useRefreshControl({
  onRefresh,
  refreshing: externalRefreshing,
  tintColor = COLORS.primary,
  colors = [COLORS.primary],
}: UseRefreshControlOptions) {
  const [internalRefreshing, setInternalRefreshing] = useState(false);

  const refreshing = externalRefreshing ?? internalRefreshing;

  const handleRefresh = useCallback(async () => {
    if (externalRefreshing !== undefined) {
      await onRefresh();
      return;
    }

    setInternalRefreshing(true);
    try {
      await onRefresh();
    } finally {
      setInternalRefreshing(false);
    }
  }, [onRefresh, externalRefreshing]);

  const refreshControl = (
    <RefreshControl
      refreshing={refreshing}
      onRefresh={handleRefresh}
      tintColor={tintColor}
      colors={colors}
    />
  );

  return {
    refreshControl,
    refreshing,
    refresh: handleRefresh,
  };
}

