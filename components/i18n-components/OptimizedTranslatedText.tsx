import React, { useMemo } from 'react';
import { Text, TextStyle } from 'react-native';
import { useI18n } from '../../hooks/i18n-hooks/useI18n';

// ============================================================================
// TYPES
// ============================================================================

interface OptimizedTranslatedTextProps {
  translationKey: string;
  values?: Record<string, any>;
  style?: TextStyle;
  numberOfLines?: number;
  ellipsizeMode?: 'head' | 'middle' | 'tail' | 'clip';
  allowFontScaling?: boolean;
  adjustsFontSizeToFit?: boolean;
  minimumFontScale?: number;
  maximumFontScale?: number;
  onPress?: () => void;
  onLongPress?: () => void;
  selectable?: boolean;
  accessibilityLabel?: string;
  accessibilityHint?: string;
  accessibilityRole?: string;
  testID?: string;
}

// ============================================================================
// MAIN EXPORTED COMPONENT
// ============================================================================

export const OptimizedTranslatedText: React.FC<OptimizedTranslatedTextProps> = ({
  translationKey,
  values,
  style,
  numberOfLines,
  ellipsizeMode = 'tail',
  allowFontScaling = true,
  adjustsFontSizeToFit = false,
  minimumFontScale = 0.5,
  maximumFontScale = 2.0,
  onPress,
  onLongPress,
  selectable = false,
  accessibilityLabel,
  accessibilityHint,
  accessibilityRole,
  testID,
}) => {
  const { t, isRTL } = useI18n();

  // Memoized translated text
  const translatedText = useMemo(() => {
    try {
      return t(translationKey, values);
    } catch (error) {
      console.warn(`Translation key not found: ${translationKey}`, error);
      return translationKey;
    }
  }, [t, translationKey, values]);

  // Memoized text style with RTL support
  const textStyle = useMemo(() => {
    const baseStyle: TextStyle = {
      textAlign: isRTL ? 'right' : 'left',
      writingDirection: isRTL ? 'rtl' : 'ltr',
    };

    return [baseStyle, style];
  }, [isRTL, style]);

  return (
    <Text
      style={textStyle}
      numberOfLines={numberOfLines}
      ellipsizeMode={ellipsizeMode}
      allowFontScaling={allowFontScaling}
      adjustsFontSizeToFit={adjustsFontSizeToFit}
      minimumFontScale={minimumFontScale}
      maximumFontScale={maximumFontScale}
      onPress={onPress}
      onLongPress={onLongPress}
      selectable={selectable}
      accessible={true}
      accessibilityLabel={accessibilityLabel || translatedText}
      accessibilityHint={accessibilityHint}
      accessibilityRole={accessibilityRole}
      testID={testID}
    >
      {translatedText}
    </Text>
  );
}; 