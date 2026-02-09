import { useTranslation } from 'react-i18next';
import { useMemo } from 'react';
import { getCurrentLanguage, isRTL, getTextDirection } from '../../utils/i18n/i18nConfig';

export interface UseI18nReturn {
  t: (key: string, options?: any) => string;
  i18n: any;
  isRTL: boolean;
  currentLanguage: string;
  textDirection: 'ltr' | 'rtl';
  changeLanguage: (language: string) => Promise<void>;
}

export const useI18n = (): UseI18nReturn => {
  const { t, i18n } = useTranslation();
  const currentLanguage = getCurrentLanguage();
  
  const rtl = useMemo(() => isRTL(), [currentLanguage]);
  const textDirection = useMemo(() => getTextDirection(), [currentLanguage]);

  const changeLanguage = async (language: string): Promise<void> => {
    try {
      await i18n.changeLanguage(language);
    } catch (error) {
      console.error('Failed to change language:', error);
    }
  };

  return {
    t,
    i18n,
    isRTL: rtl,
    currentLanguage,
    textDirection,
    changeLanguage,
  };
}; 