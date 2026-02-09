// UI Component Types

import { ViewStyle, TextStyle, ImageStyle } from 'react-native';

export interface BaseComponentProps {
  style?: ViewStyle | TextStyle | ImageStyle;
  testID?: string;
  accessibilityLabel?: string;
  accessibilityHint?: string;
}

export interface ButtonVariant {
  primary: 'primary';
  secondary: 'secondary';
  outline: 'outline';
  danger: 'danger';
}

export interface ButtonSize {
  small: 'small';
  medium: 'medium';
  large: 'large';
}

export type ButtonVariantType = ButtonVariant[keyof ButtonVariant];
export type ButtonSizeType = ButtonSize[keyof ButtonSize];

export interface ButtonProps extends BaseComponentProps {
  title: string;
  onPress: () => void;
  variant?: ButtonVariantType;
  size?: ButtonSizeType;
  disabled?: boolean;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export interface InputProps extends BaseComponentProps {
  label?: string;
  placeholder?: string;
  value?: string;
  onChangeText?: (text: string) => void;
  error?: string;
  disabled?: boolean;
  secureTextEntry?: boolean;
  keyboardType?: 'default' | 'email-address' | 'numeric' | 'phone-pad';
  autoCapitalize?: 'none' | 'sentences' | 'words' | 'characters';
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  multiline?: boolean;
  numberOfLines?: number;
}

export interface CardProps extends BaseComponentProps {
  variant?: 'default' | 'elevated' | 'outlined';
  onPress?: () => void;
  children: React.ReactNode;
}

export interface LoadingProps extends BaseComponentProps {
  message?: string;
  size?: 'small' | 'large';
  color?: string;
}

export interface ErrorMessageProps extends BaseComponentProps {
  message: string;
  onRetry?: () => void;
  retryLabel?: string;
}

export interface EmptyStateProps extends BaseComponentProps {
  title: string;
  message?: string;
  icon?: React.ReactNode;
  actionLabel?: string;
  onAction?: () => void;
}

export interface SkeletonProps extends BaseComponentProps {
  width?: number | string;
  height?: number;
  borderRadius?: number;
  variant?: 'text' | 'circular' | 'rectangular';
}

export interface BadgeProps extends BaseComponentProps {
  label: string;
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
  size?: 'small' | 'medium' | 'large';
}

export interface AvatarProps extends BaseComponentProps {
  source?: { uri: string } | number;
  name?: string;
  size?: number;
  variant?: 'circular' | 'rounded' | 'square';
}

export interface ListItemProps extends BaseComponentProps {
  title: string;
  subtitle?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  onPress?: () => void;
  disabled?: boolean;
  selected?: boolean;
}

export interface SectionHeaderProps extends BaseComponentProps {
  title: string;
  subtitle?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export interface DividerProps extends BaseComponentProps {
  orientation?: 'horizontal' | 'vertical';
  variant?: 'solid' | 'dashed';
}

export interface ChipProps extends BaseComponentProps {
  label: string;
  selected?: boolean;
  onPress?: () => void;
  onClose?: () => void;
  variant?: 'default' | 'outlined';
}

export interface ProgressBarProps extends BaseComponentProps {
  progress: number; // 0-100
  color?: string;
  backgroundColor?: string;
  height?: number;
  showLabel?: boolean;
}

export interface SwitchProps extends BaseComponentProps {
  value: boolean;
  onValueChange: (value: boolean) => void;
  disabled?: boolean;
  trackColor?: { false: string; true: string };
  thumbColor?: string;
}

export interface CheckboxProps extends BaseComponentProps {
  checked: boolean;
  onPress: () => void;
  disabled?: boolean;
  label?: string;
  size?: 'small' | 'medium' | 'large';
}

export interface RadioButtonProps extends BaseComponentProps {
  selected: boolean;
  onPress: () => void;
  disabled?: boolean;
  label?: string;
}

export interface ModalProps extends BaseComponentProps {
  visible: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  showCloseButton?: boolean;
  animationType?: 'fade' | 'slide';
}

export interface BottomSheetProps extends BaseComponentProps {
  visible: boolean;
  onClose: () => void;
  children: React.ReactNode;
  snapPoints?: number[];
}

export interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  position?: 'top' | 'bottom';
}

export interface TooltipProps extends BaseComponentProps {
  text: string;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

