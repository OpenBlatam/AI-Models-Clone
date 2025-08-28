import React, { useMemo } from 'react';
import { Text, TextProps, StyleSheet } from 'react-native';
import { useWindowDimensions } from 'react-native';
import { t } from '../../utils/i18n/i18nConfig';

interface OptimizedAccessibleTextProps extends TextProps {
  children: string;
  variant?: 'body' | 'title' | 'caption' | 'label';
  scaleWithSystem?: boolean;
  supportsRTL?: boolean;
  maxFontSizeMultiplier?: number;
}

const TEXT_VARIANTS = {
  body: {
    fontSize: 16,
    lineHeight: 24,
    fontWeight: '400' as const,
  },
  title: {
    fontSize: 20,
    lineHeight: 28,
    fontWeight: '600' as const,
  },
  caption: {
    fontSize: 14,
    lineHeight: 20,
    fontWeight: '400' as const,
  },
  label: {
    fontSize: 12,
    lineHeight: 16,
    fontWeight: '500' as const,
  },
} as const;

export const OptimizedAccessibleText: React.FC<OptimizedAccessibleTextProps> = ({
  children,
  variant = 'body',
  scaleWithSystem = true,
  supportsRTL = true,
  maxFontSizeMultiplier = 2.0,
  style,
  ...props
}) => {
  const { fontScale } = useWindowDimensions();

  const textStyle = useMemo(() => {
    const baseStyle = TEXT_VARIANTS[variant];
    const scaledFontSize = scaleWithSystem 
      ? baseStyle.fontSize * Math.min(fontScale, maxFontSizeMultiplier)
      : baseStyle.fontSize;

    return [
      baseStyle,
      { fontSize: scaledFontSize },
      supportsRTL && { writingDirection: 'auto' },
      style,
    ];
  }, [variant, scaleWithSystem, fontScale, maxFontSizeMultiplier, supportsRTL, style]);

  return (
    <Text
      style={textStyle}
      allowFontScaling={scaleWithSystem}
      maxFontSizeMultiplier={maxFontSizeMultiplier}
      accessible={true}
      accessibilityRole="text"
      {...props}
    >
      {children}
    </Text>
  );
};

const styles = StyleSheet.create({
  text: {
    color: '#000000',
  },
}); 