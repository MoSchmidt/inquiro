import { defineStore } from 'pinia';
import { login as loginApi, signup as signupApi } from '@/services/auth';

interface User {
  user_id: number;
  username: string;
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  loading: boolean;
  error: string | null;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    accessToken: null,
    refreshToken: null,
    user: null,
    loading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },

  actions: {
    async login(username: string, password: string) {
      this.loading = true;
      this.error = null;

      try {
        const { access_token, refresh_token, user } = await loginApi(
          username,
          password
        );

        this.accessToken = access_token;
        this.refreshToken = refresh_token;
        this.user = user;

        return user;
      } catch (err) {
        this.error = 'Login failed.';
        console.error(err);
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async signup(username: string, password: string) {
      this.loading = true;
      this.error = null;

      try {
        await signupApi(username);
        // domain decision: auto-login after signup
        return await this.login(username, password);
      } catch (err) {
        this.error = 'Signup failed.';
        console.error(err);
        throw err;
      } finally {
        this.loading = false;
      }
    },

    logout() {
      this.accessToken = null;
      this.refreshToken = null;
      this.user = null;
      this.error = null;
    },

    reset() {
      this.$reset();
    },
  },
});
