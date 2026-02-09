import React, { useMemo } from 'react';
import { View, TouchableOpacity, Text, StyleSheet, ScrollView, ViewStyle } from 'react-native';
import { useI18n } from '../../hooks/i18n-hooks/useI18n';
import { getAllLanguages, getCurrentLanguage, changeLanguage } from '../../utils/i18n/i18nConfig';

interface LanguageConfig {
  code: string;
  name: string;
  nativeName: string;
  direction: 'ltr' | 'rtl';
  isRTL: boolean;
}

interface OptimizedLanguageSelectorProps {
  onLanguageChange?: (languageCode: string) => void;
  style?: ViewStyle;
  showNativeNames?: boolean;
  showFlags?: boolean;
  maxHeight?: number;
}

export const OptimizedLanguageSelector: React.FC<OptimizedLanguageSelectorProps> = ({
  onLanguageChange,
  style,
  showNativeNames = true,
  showFlags = true,
  maxHeight = 300,
}) => {
  const { currentLanguage, isRTL } = useI18n();
  const languages = useMemo(() => getAllLanguages(), []);

  const handleLanguageSelect = async (languageCode: string) => {
    try {
      await changeLanguage(languageCode);
      onLanguageChange?.(languageCode);
    } catch (error) {
      console.error('Failed to change language:', error);
    }
  };

  const getFlagEmoji = (languageCode: string): string => {
    const flagMap: Record<string, string> = {
      en: '🇺🇸',
      es: '🇪🇸',
      fr: '🇫🇷',
      de: '🇩🇪',
      pt: '🇵🇹',
      ar: '🇸🇦',
      zh: '🇨🇳',
      ja: '🇯🇵',
      ko: '🇰🇷',
      ru: '🇷🇺',
    };
    return flagMap[languageCode] || '🌐';
  };

  const getLanguageDisplayName = (language: any): string => {
    if (showNativeNames) {
      return language.nativeName;
    }
    return language.name;
  };

  return (
    <View style={[styles.container, style]}>
      <ScrollView 
        style={[styles.scrollView, { maxHeight }]}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {languages.map((language) => (
          <TouchableOpacity
            key={language.code}
            style={[
              styles.languageItem,
              currentLanguage === language.code && styles.selectedLanguage,
              { flexDirection: isRTL ? 'row-reverse' : 'row' }
            ]}
            onPress={() => handleLanguageSelect(language.code)}
            accessible={true}
            accessibilityLabel={`Select ${language.name} language`}
            accessibilityRole="button"
            accessibilityState={{ selected: currentLanguage === language.code }}
          >
            {showFlags && (
              <Text style={styles.flag}>{getFlagEmoji(language.code)}</Text>
            )}
            <View style={[styles.languageInfo, { alignItems: isRTL ? 'flex-end' : 'flex-start' }]}>
              <Text style={[
                styles.languageName,
                currentLanguage === language.code && styles.selectedLanguageText
              ]}>
                {getLanguageDisplayName(language)}
              </Text>
              {showNativeNames && language.code !== 'en' && (
                <Text style={[
                  styles.languageNativeName,
                  currentLanguage === language.code && styles.selectedLanguageText
                ]}>
                  {language.name}
                </Text>
              )}
            </View>
            {currentLanguage === language.code && (
              <Text style={styles.checkmark}>✓</Text>
            )}
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingVertical: 8,
  },
  languageItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  selectedLanguage: {
    backgroundColor: '#f8f9fa',
  },
  flag: {
    fontSize: 20,
    marginRight: 12,
  },
  languageInfo: {
    flex: 1,
  },
  languageName: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333333',
  },
  languageNativeName: {
    fontSize: 12,
    color: '#666666',
    marginTop: 2,
  },
  selectedLanguageText: {
    color: '#007AFF',
    fontWeight: '600',
  },
  checkmark: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: 'bold',
  },
}); 