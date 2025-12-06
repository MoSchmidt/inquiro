import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { login as loginApi, signup } from './auth';

export function useAuthService() {
  const authStore = useAuthStore();

  const isAuthenticated = computed(() => authStore.isAuthenticated);
  const user = computed(() => authStore.user);

  const loginUser = async (username: string, password: string) => {
    const { access_token, refresh_token, user } = await loginApi(username, password);
    authStore.setAuth({
      accessToken: access_token,
      refreshToken: refresh_token,
      user,
    });

    return { access_token, refresh_token, user };
  };

  const logoutUser = () => {
    authStore.clearAuth();
  };

  const signupUser = async (username: string, password: string) => {
    await signup(username);
    return loginUser(username, password);
  };

  return {
    isAuthenticated,
    user,
    loginUser,
    logoutUser,
    signupUser,
  };
}
