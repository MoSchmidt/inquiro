import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { login as loginApi, signup as signupApi } from '@/services/auth';

interface User {
  user_id: number;
  username: string;
}

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(null);
  const refreshToken = ref<string | null>(null);
  const user = ref<User | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const isAuthenticated = computed(() => !!accessToken.value);

  async function login(username: string, password: string) {
    loading.value = true;
    error.value = null;

    try {
      const { access_token, refresh_token, user: userFromApi } =
        await loginApi(username, password);

      accessToken.value = access_token;
      refreshToken.value = refresh_token;
      user.value = userFromApi;

      return userFromApi;
    } catch (err) {
      error.value = 'Login failed.';
      console.error(err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function signup(username: string, password: string) {
    loading.value = true;
    error.value = null;

    try {
      await signupApi(username);
      // domain decision: auto-login after signup
      return await login(username, password);
    } catch (err) {
      error.value = 'Signup failed.';
      console.error(err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function logout() {
    accessToken.value = null;
    refreshToken.value = null;
    user.value = null;
    error.value = null;
  }

  function reset() {
    accessToken.value = null;
    refreshToken.value = null;
    user.value = null;
    loading.value = false;
    error.value = null;
  }

  return {
    // state
    accessToken,
    refreshToken,
    user,
    loading,
    error,

    // getters
    isAuthenticated,

    // actions
    login,
    signup,
    logout,
    reset,
  };
},
  {
    persist: {
      key: 'auth',
      storage: sessionStorage,
      pick: ['accessToken', 'refreshToken', 'user'],
    },
  });
