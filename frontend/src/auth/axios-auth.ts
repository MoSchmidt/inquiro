import axios from "axios";
import type { AxiosRequestHeaders } from "axios";
import { useAuthStore } from "../stores/auth";

export const apiAxios = axios.create();

apiAxios.interceptors.request.use((config) => {
  const auth = useAuthStore();

  if (auth.accessToken) {
    const headers = (config.headers ?? {}) as AxiosRequestHeaders;

    headers.Authorization = `Bearer ${auth.accessToken}`;

    config.headers = headers;
  }

  return config;
});
