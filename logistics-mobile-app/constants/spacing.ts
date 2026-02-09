// Spacing Scale (8px base)
export const SPACING = {
  XS: 4,
  SM: 8,
  MD: 16,
  LG: 24,
  XL: 32,
  XXL: 48,
  XXXL: 64,
} as const;

// Border Radius
export const RADIUS = {
  XS: 4,
  SM: 8,
  MD: 12,
  LG: 16,
  XL: 20,
  FULL: 9999,
} as const;

// Border Width
export const BORDER_WIDTH = {
  THIN: 0.5,
  NORMAL: 1,
  THICK: 2,
} as const;

// Shadow Elevations
export const ELEVATION = {
  NONE: 0,
  LOW: 2,
  MEDIUM: 4,
  HIGH: 8,
  VERY_HIGH: 16,
} as const;

// Z-Index Layers
export const Z_INDEX = {
  BASE: 0,
  DROPDOWN: 1000,
  STICKY: 1020,
  FIXED: 1030,
  MODAL_BACKDROP: 1040,
  MODAL: 1050,
  POPOVER: 1060,
  TOOLTIP: 1070,
  NOTIFICATION: 1080,
} as const;


