"use client";
import React, { Suspense, memo } from 'react';
import { View, ActivityIndicator, FlatList, ListRenderItemInfo } from 'react-native';
import type { Video } from './types';

const VideoItem = React.lazy(() => import('./VideoItem'));

interface VideoPlayerProps {
  videos: Video[];
}

function renderItem({ item }: ListRenderItemInfo<Video>) {
  return (
    <Suspense fallback={<ActivityIndicator size="small" color="#888" />}>
      <VideoItem video={item} />
    </Suspense>
  );
}

const MemoizedRenderItem = memo(renderItem);

export const VideoPlayer: React.FC<VideoPlayerProps> = ({ videos }) => (
  <FlatList
    data={videos}
    keyExtractor={item => item.id}
    renderItem={MemoizedRenderItem}
    removeClippedSubviews
    maxToRenderPerBatch={5}
    windowSize={10}
    getItemLayout={(_, index) => ({ length: 100, offset: 100 * index, index })}
  />
);       