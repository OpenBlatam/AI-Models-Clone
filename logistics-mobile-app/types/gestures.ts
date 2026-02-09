// Gesture Types

export interface GestureState {
  translationX: number;
  translationY: number;
  velocityX: number;
  velocityY: number;
  state: number;
}

export interface PanGestureHandlerEvent {
  nativeEvent: GestureState;
}

export interface PinchGestureHandlerEvent {
  nativeEvent: {
    scale: number;
    focalX: number;
    focalY: number;
    velocity: number;
    state: number;
  };
}

export interface RotationGestureHandlerEvent {
  nativeEvent: {
    rotation: number;
    anchorX: number;
    anchorY: number;
    velocity: number;
    state: number;
  };
}

export interface TapGestureHandlerEvent {
  nativeEvent: {
    x: number;
    y: number;
    absoluteX: number;
    absoluteY: number;
    state: number;
  };
}

export interface LongPressGestureHandlerEvent {
  nativeEvent: {
    x: number;
    y: number;
    absoluteX: number;
    absoluteY: number;
    duration: number;
    state: number;
  };
}

export interface SwipeGestureConfig {
  direction: 'left' | 'right' | 'up' | 'down';
  velocityThreshold?: number;
  distanceThreshold?: number;
}

export interface GestureHandlerConfig {
  enabled?: boolean;
  simultaneousHandlers?: React.Ref<any>[];
  waitFor?: React.Ref<any>[];
  hitSlop?: {
    left?: number;
    right?: number;
    top?: number;
    bottom?: number;
  };
  activeOffsetX?: number | number[];
  activeOffsetY?: number | number[];
  failOffsetX?: number | number[];
  failOffsetY?: number | number[];
}

