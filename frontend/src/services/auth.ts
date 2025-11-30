import { AuthenticationApi } from '@/api';
import { apiAxios } from '@/auth/axios-auth';

const authApi = new AuthenticationApi(undefined, undefined, apiAxios);

export async function login(username: string) {
  const response = await authApi.loginAuthLoginPost({ username });
  return response.data;
}
