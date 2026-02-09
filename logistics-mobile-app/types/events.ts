// Event Types

export interface BaseEvent {
  type: string;
  timestamp: string;
  source?: string;
}

export interface TouchEvent {
  nativeEvent: {
    pageX: number;
    pageY: number;
    locationX: number;
    locationY: number;
  };
}

export interface GestureEvent {
  nativeEvent: {
    translationX: number;
    translationY: number;
    velocityX: number;
    velocityY: number;
    state: number;
  };
}

export interface SwipeEvent {
  direction: 'left' | 'right' | 'up' | 'down';
  velocity: number;
}

export interface KeyboardEvent {
  height: number;
  duration: number;
  easing: string;
}

export interface NetworkEvent extends BaseEvent {
  type: 'network_change';
  isConnected: boolean;
  isInternetReachable: boolean;
  type: string;
}

export interface AppStateEvent extends BaseEvent {
  type: 'app_state_change';
  state: 'active' | 'background' | 'inactive';
}

export interface ErrorEvent extends BaseEvent {
  type: 'error';
  error: Error;
  context?: Record<string, unknown>;
  severity?: 'low' | 'medium' | 'high' | 'critical';
}

export interface AnalyticsEvent extends BaseEvent {
  type: 'analytics';
  eventName: string;
  properties?: Record<string, unknown>;
  userId?: string;
}

export interface NavigationEvent extends BaseEvent {
  type: 'navigation';
  route: string;
  params?: Record<string, unknown>;
  action: 'push' | 'pop' | 'replace' | 'reset';
}

export interface FormEvent extends BaseEvent {
  type: 'form';
  formName: string;
  action: 'submit' | 'change' | 'blur' | 'focus' | 'reset';
  field?: string;
  value?: unknown;
}

export interface APIEvent extends BaseEvent {
  type: 'api';
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  url: string;
  status?: number;
  duration?: number;
  error?: Error;
}

export type AppEvent =
  | NetworkEvent
  | AppStateEvent
  | ErrorEvent
  | AnalyticsEvent
  | NavigationEvent
  | FormEvent
  | APIEvent;

export interface EventHandler<T extends AppEvent = AppEvent> {
  (event: T): void;
}

export interface EventListener {
  type: string;
  handler: EventHandler;
  once?: boolean;
}

