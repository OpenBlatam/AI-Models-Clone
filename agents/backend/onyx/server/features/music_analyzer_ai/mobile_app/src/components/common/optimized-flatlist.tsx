import React, { memo, useMemo, useCallback } from 'react';
import { FlatList, FlatListProps, ListRenderItem, Platform } from 'react-native';

interface OptimizedFlatListProps<T> extends Omit<FlatListProps<T>, 'removeClippedSubviews' | 'maxToRenderPerBatch' | 'windowSize' | 'initialNumToRender' | 'getItemLayout' | 'updateCellsBatchingPeriod'> {
  data: T[];
  renderItem: ListRenderItem<T>;
  keyExtractor: (item: T, index: number) => string;
  itemHeight?: number;
  estimatedItemHeight?: number;
  enableOptimizations?: boolean;
}

function OptimizedFlatListComponent<T>({
  data,
  renderItem,
  keyExtractor,
  itemHeight,
  estimatedItemHeight,
  enableOptimizations = true,
  ...props
}: OptimizedFlatListProps<T>) {