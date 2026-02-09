// Animation Presets
export const ANIMATION_PRESETS = {
  // Spring Configurations
  SPRING: {
    GENTLE: {
      damping: 20,
      stiffness: 90,
    },
    BOUNCY: {
      damping: 10,
      stiffness: 100,
    },
    SMOOTH: {
      damping: 30,
      stiffness: 200,
    },
  },

  // Timing Configurations
  TIMING: {
    FAST: {
      duration: 150,
    },
    NORMAL: {
      duration: 300,
    },
    SLOW: {
      duration: 500,
    },
  },

  // Easing Functions
  EASING: {
    EASE_IN: 'ease-in',
    EASE_OUT: 'ease-out',
    EASE_IN_OUT: 'ease-in-out',
    LINEAR: 'linear',
  },
} as const;

// Animation Values
export const ANIMATION_VALUES = {
  SCALE: {
    PRESSED: 0.95,
    HOVER: 1.05,
    NORMAL: 1,
  },
  OPACITY: {
    HIDDEN: 0,
    VISIBLE: 1,
    DISABLED: 0.5,
  },
  TRANSLATE: {
    HIDDEN: -100,
    VISIBLE: 0,
  },
} as const;

// Gesture Thresholds
export const GESTURE_THRESHOLDS = {
  SWIPE: {
    VELOCITY: 500,
    DISTANCE: 50,
  },
  LONG_PRESS: 500, // milliseconds
  DOUBLE_TAP: 300, // milliseconds
} as const;


