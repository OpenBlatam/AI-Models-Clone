import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface AuthState {
  isAuthenticated: boolean;
  artistId: string | null;
  apiKey: string | null;
  setAuth: (artistId: string, apiKey: string) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      artistId: null,
      apiKey: null,
      setAuth: (artistId, apiKey) =>
        set({
          isAuthenticated: true,
          artistId,
          apiKey,
        }),
      clearAuth: () =>
        set({
          isAuthenticated: false,
          artistId: null,
          apiKey: null,
        }),
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);


