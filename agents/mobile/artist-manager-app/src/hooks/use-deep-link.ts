import { useEffect, useState } from 'react';
import * as Linking from 'expo-linking';

interface DeepLinkState {
  url: string | null;
  params: Record<string, string> | null;
}

/**
 * Hook for handling deep links
 */
export function useDeepLink() {
  const [deepLink, setDeepLink] = useState<DeepLinkState>({
    url: null,
    params: null,
  });

  useEffect(() => {
    // Get initial URL
    Linking.getInitialURL().then((url) => {
      if (url) {
        const parsed = Linking.parse(url);
        setDeepLink({
          url,
          params: parsed.queryParams as Record<string, string>,
        });
      }
    });

    // Listen for deep links
    const subscription = Linking.addEventListener('url', (event) => {
      const parsed = Linking.parse(event.url);
      setDeepLink({
        url: event.url,
        params: parsed.queryParams as Record<string, string>,
      });
    });

    return () => {
      subscription.remove();
    };
  }, []);

  const openURL = async (url: string) => {
    const canOpen = await Linking.canOpenURL(url);
    if (canOpen) {
      await Linking.openURL(url);
    }
  };

  return {
    ...deepLink,
    openURL,
  };
}


