// Animation Types

export interface AnimationConfig {
  duration?: number;
  delay?: number;
  easing?: string;
}

export interface SpringConfig {
  damping?: number;
  stiffness?: number;
  mass?: number;
  overshootClamping?: boolean;
  restDisplacementThreshold?: number;
  restSpeedThreshold?: number;
}

export interface TimingConfig extends AnimationConfig {
  easing?: (value: number) => number;
}

export interface AnimationValue {
  value: number;
  setValue: (value: number) => void;
  setValueWithAnimation: (value: number, config?: AnimationConfig) => void;
}

export interface AnimatedStyle {
  transform?: Array<{
    translateX?: number;
    translateY?: number;
    scale?: number;
    scaleX?: number;
    scaleY?: number;
    rotate?: string;
    rotateX?: string;
    rotateY?: string;
  }>;
  opacity?: number;
  width?: number;
  height?: number;
  backgroundColor?: string;
  borderRadius?: number;
}

export interface AnimationPreset {
  name: string;
  config: SpringConfig | TimingConfig;
}

export interface TransitionConfig {
  type: 'fade' | 'slide' | 'scale' | 'none';
  duration?: number;
  delay?: number;
}

export interface LayoutAnimationConfig {
  duration?: number;
  create?: TransitionConfig;
  update?: TransitionConfig;
  delete?: TransitionConfig;
}

