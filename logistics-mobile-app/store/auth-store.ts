import { create } from 'zustand';
import * as SecureStore from 'expo-secure-store';

interface AuthState {
  isAuthenticated: boolean;
  token: string | null;
  user: {
    id: string;
    email: string;
    name: string;
  } | null;
  setAuth: (token: string, user: { id: string; email: string; name: string }) => Promise<void>;
  logout: () => Promise<void>;
  initialize: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  token: null,
  user: null,

  setAuth: async (token, user) => {
    await SecureStore.setItemAsync('auth_token', token);
    set({ isAuthenticated: true, token, user });
  },

  logout: async () => {
    await SecureStore.deleteItemAsync('auth_token');
    set({ isAuthenticated: false, token: null, user: null });
  },

  initialize: async () => {
    const token = await SecureStore.getItemAsync('auth_token');
    if (token) {
      set({ isAuthenticated: true, token });
    }
  },
}));


