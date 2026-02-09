import { useCallback } from 'react';
import Toast from 'react-native-toast-message';
import { haptics } from '@/utils/haptics';

interface ToastOptions {
  text2?: string;
  visibilityTime?: number;
  autoHide?: boolean;
  topOffset?: number;
  bottomOffset?: number;
}

export function useToast() {
  const showSuccess = useCallback((text1: string, options?: ToastOptions) => {
    haptics.success();
    Toast.show({
      type: 'success',
      text1,
      ...options,
    });
  }, []);

  const showError = useCallback((text1: string, options?: ToastOptions) => {
    haptics.error();
    Toast.show({
      type: 'error',
      text1,
      ...options,
    });
  }, []);

  const showInfo = useCallback((text1: string, options?: ToastOptions) => {
    haptics.selection();
    Toast.show({
      type: 'info',
      text1,
      ...options,
    });
  }, []);

  const hide = useCallback(() => {
    Toast.hide();
  }, []);

  return {
    showSuccess,
    showError,
    showInfo,
    hide,
  };
}


