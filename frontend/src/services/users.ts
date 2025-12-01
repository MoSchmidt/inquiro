import { UsersApi } from '@/api';
import { apiAxios } from '@/auth/axios-auth';

const usersApi = new UsersApi(undefined, undefined, apiAxios);

export async function createUser(username: string) {
    // The generated API expects a UserCreate payload with `username`
    const payload = { username };
    const resp = await usersApi.createUserUsersPost(payload as any);
    return resp.data;
}

export async function getCurrentUser() {
    const resp = await usersApi.getCurrentUserProfileUsersMeGet();
    return resp.data;
}

export default {
    createUser,
    getCurrentUser,
};
