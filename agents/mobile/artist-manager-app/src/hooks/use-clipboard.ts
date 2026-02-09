import { useState, useCallback } from 'react';
import * as Clipboard from 'expo-clipboard';

/**
 * Hook for clipboard operations
 */
export function useClipboard() {
  const [clipboardText, setClipboardTextState] = useState<string>('');

  const getClipboardText = useCallback(async () => {
    try {
      const text = await Clipboard.getStringAsync();
      setClipboardTextState(text);
      return text;
    } catch (error) {
      console.error('Error reading clipboard:', error);
      return '';
    }
  }, []);

  const setClipboardText = useCallback(async (text: string) => {
    try {
      await Clipboard.setStringAsync(text);
      setClipboardTextState(text);
    } catch (error) {
      console.error('Error setting clipboard:', error);
    }
  }, []);

  return {
    clipboardText,
    getClipboardText,
    setClipboardText,
  };
}

