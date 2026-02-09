import { ReactNode } from 'react';
import Toast from 'react-native-toast-message';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Colors } from '@/constants/colors';

interface ToastProviderProps {
  children: ReactNode;
}

export function ToastProvider({ children }: ToastProviderProps) {
  const { isDark } = useColorScheme();
  const colors = isDark ? Colors.dark : Colors.light;

  return (
    <>
      {children}
      <Toast
        config={{
          success: (props) => (
            <Toast.BaseToast
              {...props}
              style={{ borderLeftColor: colors.success }}
              contentContainerStyle={{ paddingHorizontal: 15 }}
              text1Style={{
                fontSize: 15,
                fontWeight: '600',
                color: colors.text,
              }}
              text2Style={{
                fontSize: 13,
                color: colors.icon,
              }}
            />
          ),
          error: (props) => (
            <Toast.ErrorToast
              {...props}
              style={{ borderLeftColor: colors.error }}
              contentContainerStyle={{ paddingHorizontal: 15 }}
              text1Style={{
                fontSize: 15,
                fontWeight: '600',
                color: colors.text,
              }}
              text2Style={{
                fontSize: 13,
                color: colors.icon,
              }}
            />
          ),
          info: (props) => (
            <Toast.BaseToast
              {...props}
              style={{ borderLeftColor: colors.primary }}
              contentContainerStyle={{ paddingHorizontal: 15 }}
              text1Style={{
                fontSize: 15,
                fontWeight: '600',
                color: colors.text,
              }}
              text2Style={{
                fontSize: 13,
                color: colors.icon,
              }}
            />
          ),
        }}
      />
    </>
  );
}


