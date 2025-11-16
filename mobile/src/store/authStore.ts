import { create } from 'zustand';
import * as SecureStore from 'expo-secure-store';

interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  setAuth: (user: User, accessToken: string) => Promise<void>;
  clearAuth: () => Promise<void>;
  loadAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  isAuthenticated: false,

  setAuth: async (user, accessToken) => {
    await SecureStore.setItemAsync('user', JSON.stringify(user));
    await SecureStore.setItemAsync('accessToken', accessToken);
    set({ user, accessToken, isAuthenticated: true });
  },

  clearAuth: async () => {
    await SecureStore.deleteItemAsync('user');
    await SecureStore.deleteItemAsync('accessToken');
    set({ user: null, accessToken: null, isAuthenticated: false });
  },

  loadAuth: async () => {
    try {
      const userStr = await SecureStore.getItemAsync('user');
      const accessToken = await SecureStore.getItemAsync('accessToken');

      if (userStr && accessToken) {
        const user = JSON.parse(userStr);
        set({ user, accessToken, isAuthenticated: true });
      }
    } catch (error) {
      console.error('Failed to load auth:', error);
    }
  },
}));
