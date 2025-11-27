import { AuthenticationApi } from '@/api';

const authApi = new AuthenticationApi();

export async function login(username: string) {
  const response = await authApi.loginAuthLoginPost({ username });
  return response.data;
}
