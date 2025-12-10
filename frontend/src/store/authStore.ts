import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi, AuthResponse, LoginData, SignupData } from '@/api/authApi';

interface User {
  id: string;
  email: string;
  name: string;
  isVerified: boolean;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;

  // Actions
  login: (data: LoginData) => Promise<void>;
  signup: (data: SignupData) => Promise<void>;
  logout: () => void;
  verifyEmail: (token: string) => Promise<void>;
  resendVerification: (email: string) => Promise<void>;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  clearError: () => void;
  reset: () => void;
}

const initialState = {
  token: null,
  user: null,
  isLoading: false,
  error: null,
  isAuthenticated: false,
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      ...initialState,

      login: async (data: LoginData) => {
        set({ isLoading: true, error: null });
        try {
          const response: AuthResponse = await authApi.login(data);
          set({
            token: response.token,
            user: response.user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          const message = error.response?.data?.message || 'Login failed. Please try again.';
          set({ isLoading: false, error: message });
          throw error;
        }
      },

      signup: async (data: SignupData) => {
        set({ isLoading: true, error: null });
        try {
          const response: AuthResponse = await authApi.signup(data);
          set({
            token: response.token,
            user: response.user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          const message = error.response?.data?.message || 'Signup failed. Please try again.';
          set({ isLoading: false, error: message });
          throw error;
        }
      },

      logout: () => {
        authApi.logout().catch(() => {});
        set(initialState);
      },

      verifyEmail: async (token: string) => {
        set({ isLoading: true, error: null });
        try {
          await authApi.verifyEmail({ token });
          const currentUser = get().user;
          if (currentUser) {
            set({ user: { ...currentUser, isVerified: true }, isLoading: false });
          }
        } catch (error: any) {
          const message = error.response?.data?.message || 'Email verification failed.';
          set({ isLoading: false, error: message });
          throw error;
        }
      },

      resendVerification: async (email: string) => {
        set({ isLoading: true, error: null });
        try {
          await authApi.resendVerification(email);
          set({ isLoading: false });
        } catch (error: any) {
          const message = error.response?.data?.message || 'Failed to resend verification email.';
          set({ isLoading: false, error: message });
          throw error;
        }
      },

      setUser: (user: User) => set({ user }),
      setToken: (token: string) => set({ token, isAuthenticated: true }),
      clearError: () => set({ error: null }),
      reset: () => set(initialState),
    }),
    {
      name: 'revisify-auth',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
