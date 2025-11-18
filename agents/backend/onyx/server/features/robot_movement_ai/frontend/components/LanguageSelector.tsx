'use client';

import { Globe } from 'lucide-react';
import { useI18nStore } from '@/lib/store/i18nStore';
import { Language } from '@/lib/i18n/translations';

export default function LanguageSelector() {
  const { language, setLanguage } = useI18nStore();

  const languages: { code: Language; name: string; flag: string }[] = [
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'en', name: 'English', flag: '🇺🇸' },
  ];

  return (
    <div className="relative group">
      <button className="flex items-center gap-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors">
        <Globe className="w-4 h-4" />
        <span className="hidden sm:inline">
          {languages.find((l) => l.code === language)?.flag} {languages.find((l) => l.code === language)?.name}
        </span>
      </button>
      <div className="absolute right-0 mt-2 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
        {languages.map((lang) => (
          <button
            key={lang.code}
            onClick={() => setLanguage(lang.code)}
            className={`w-full flex items-center gap-3 px-4 py-2 text-left hover:bg-gray-700 transition-colors ${
              language === lang.code ? 'bg-gray-700' : ''
            }`}
          >
            <span className="text-2xl">{lang.flag}</span>
            <span className="text-white">{lang.name}</span>
            {language === lang.code && (
              <span className="ml-auto text-primary-400">✓</span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}


