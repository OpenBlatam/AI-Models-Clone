// Ref Types

import { RefObject } from 'react';
import { TextInput, ScrollView, FlatList, SectionList } from 'react-native';

export interface TextInputRef extends RefObject<TextInput> {
  focus: () => void;
  blur: () => void;
  clear: () => void;
  isFocused: () => boolean;
}

export interface ScrollViewRef extends RefObject<ScrollView> {
  scrollTo: (options: { x?: number; y?: number; animated?: boolean }) => void;
  scrollToEnd: (options?: { animated?: boolean }) => void;
}

export interface FlatListRef<T> extends RefObject<FlatList<T>> {
  scrollToIndex: (params: { index: number; animated?: boolean }) => void;
  scrollToOffset: (params: { offset: number; animated?: boolean }) => void;
  scrollToEnd: (params?: { animated?: boolean }) => void;
}

export interface SectionListRef<T, S> extends RefObject<SectionList<T, S>> {
  scrollToLocation: (params: {
    sectionIndex: number;
    itemIndex: number;
    animated?: boolean;
  }) => void;
  scrollToOffset: (params: { offset: number; animated?: boolean }) => void;
}

export type RefCallback<T> = (instance: T | null) => void;

export type Ref<T> = RefObject<T> | RefCallback<T>;

