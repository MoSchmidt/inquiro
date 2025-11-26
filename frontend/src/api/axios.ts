import ax from 'axios';
import { useAuthStore } from '@/stores/auth';

const axios = ax.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

axios.interceptors.request.use((config) => {
  const auth = useAuthStore();
  if (auth.accessToken) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${auth.accessToken}`;
  }
  return config;
});

export default axios;
