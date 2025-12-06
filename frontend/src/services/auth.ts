import { AuthenticationApi, UsersApi } from '@/api';
import { apiAxios } from '@/auth/axios-auth';

const authApi = new AuthenticationApi(undefined, undefined, apiAxios);
const usersApi = new UsersApi(undefined, undefined, apiAxios);

export async function login(username: string, password: string) {
  // Call backend login endpoint with username and password.
  // The generated API model may vary; include password field if supported.
  const payload: any = { username };
  if (password !== undefined) payload.password = password;

  const response = await authApi.loginAuthLoginPost(payload);
  return response.data;
}

export async function signup(username: string) {
  // The generated backend model for creating a user expects { username }
  const response = await usersApi.createUserUsersPost({ username });
  return response.data;
}
