// Component Sizes
export const SIZES = {
  // Buttons
  BUTTON: {
    SMALL_HEIGHT: 32,
    MEDIUM_HEIGHT: 44,
    LARGE_HEIGHT: 52,
    MIN_WIDTH: 120,
  },

  // Inputs
  INPUT: {
    HEIGHT: 44,
    MIN_HEIGHT: 36,
    MAX_HEIGHT: 120,
  },

  // Icons
  ICON: {
    XS: 12,
    SM: 16,
    MD: 24,
    LG: 32,
    XL: 48,
  },

  // Avatars
  AVATAR: {
    SM: 32,
    MD: 48,
    LG: 64,
    XL: 96,
  },

  // Cards
  CARD: {
    MIN_HEIGHT: 100,
    PADDING: 16,
  },

  // Images
  IMAGE: {
    THUMBNAIL: 100,
    SMALL: 200,
    MEDIUM: 400,
    LARGE: 800,
  },

  // Badges
  BADGE: {
    HEIGHT: 20,
    MIN_WIDTH: 40,
    PADDING_HORIZONTAL: 8,
  },
} as const;

// Breakpoints (for responsive design)
export const BREAKPOINTS = {
  SM: 576,
  MD: 768,
  LG: 992,
  XL: 1200,
  XXL: 1400,
} as const;

// Screen Dimensions
export const SCREEN = {
  PADDING: 16,
  MAX_WIDTH: 1200,
  HEADER_HEIGHT: 56,
  TAB_BAR_HEIGHT: 60,
} as const;


