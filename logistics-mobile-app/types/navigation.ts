// Navigation Types

import { RouteProp, NavigationProp } from '@react-navigation/native';

export interface RootStackParamList {
  '(tabs)': undefined;
  'shipment/[id]': { id: string };
  'quote/create': undefined;
  'quote/[id]': { id: string };
  'booking/create': { quoteId?: string };
  'booking/[id]': { id: string };
  'document/[id]': { id: string };
  'document/upload/[shipmentId]': { shipmentId: string };
  'invoice/[id]': { id: string };
  'settings': undefined;
  'profile': undefined;
}

export interface TabParamList {
  index: undefined;
  shipments: undefined;
  tracking: undefined;
  alerts: undefined;
}

export type RootRouteProp<T extends keyof RootStackParamList> = RouteProp<RootStackParamList, T>;
export type RootNavigationProp<T extends keyof RootStackParamList> = NavigationProp<RootStackParamList, T>;

export interface NavigationState {
  currentRoute?: string;
  previousRoute?: string;
  params?: Record<string, unknown>;
}

export interface DeepLinkParams {
  path: string;
  params?: Record<string, string>;
}

export interface NavigationOptions {
  title?: string;
  headerShown?: boolean;
  headerTitle?: string;
  headerBackTitle?: string;
  headerRight?: () => React.ReactNode;
  headerLeft?: () => React.ReactNode;
  presentation?: 'card' | 'modal' | 'transparentModal';
  animation?: 'default' | 'fade' | 'slide_from_right' | 'slide_from_left';
}

