import { useState, useEffect } from 'react';
import * as Clipboard from 'expo-clipboard';

export function useClipboard() {
  const [clipboardContent, setClipboardContent] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    async function getClipboardContent() {
      try {
        const text = await Clipboard.getStringAsync();
        setClipboardContent(text);
      } catch (error) {
        console.error('Error reading clipboard:', error);
      }
    }

    getClipboardContent();
  }, []);

  async function copyToClipboard(text: string) {
    try {
      setIsLoading(true);
      await Clipboard.setStringAsync(text);
      setClipboardContent(text);
      return true;
    } catch (error) {
      console.error('Error copying to clipboard:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  }

  async function readClipboard() {
    try {
      setIsLoading(true);
      const text = await Clipboard.getStringAsync();
      setClipboardContent(text);
      return text;
    } catch (error) {
      console.error('Error reading clipboard:', error);
      return '';
    } finally {
      setIsLoading(false);
    }
  }

  return {
    clipboardContent,
    isLoading,
    copyToClipboard,
    readClipboard,
  };
}


