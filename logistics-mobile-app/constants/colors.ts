// Color Palette
export const Colors = {
  // Primary Colors
  primary: '#007AFF',
  primaryDark: '#0051D5',
  primaryLight: '#5AC8FA',

  // Secondary Colors
  secondary: '#5856D6',
  secondaryDark: '#3634A3',
  secondaryLight: '#7D7AE8',

  // Status Colors
  success: '#34C759',
  successDark: '#248A3D',
  successLight: '#5AD27A',
  warning: '#FF9500',
  warningDark: '#CC7700',
  warningLight: '#FFB340',
  error: '#FF3B30',
  errorDark: '#CC2E26',
  errorLight: '#FF6961',
  info: '#007AFF',
  infoDark: '#0051D5',
  infoLight: '#5AC8FA',

  // Neutral Colors
  background: '#F2F2F7',
  surface: '#FFFFFF',
  surfaceSecondary: '#F9F9F9',
  text: '#000000',
  textSecondary: '#8E8E93',
  textTertiary: '#C7C7CC',
  border: '#E5E5EA',
  divider: '#C6C6C8',

  // Overlay Colors
  overlay: 'rgba(0, 0, 0, 0.5)',
  overlayLight: 'rgba(0, 0, 0, 0.2)',
  overlayDark: 'rgba(0, 0, 0, 0.8)',

  // Transparent
  transparent: 'transparent',
} as const;

// Color Maps for Status
export const STATUS_COLORS = {
  pending: Colors.warning,
  quoted: Colors.info,
  booked: Colors.secondary,
  in_transit: Colors.success,
  in_customs: Colors.warning,
  delivered: Colors.success,
  delayed: Colors.error,
  cancelled: Colors.textSecondary,
  exception: Colors.error,
} as const;

// Color Maps for Severity
export const SEVERITY_COLORS = {
  low: Colors.success,
  medium: Colors.warning,
  high: Colors.error,
  critical: Colors.errorDark,
} as const;

