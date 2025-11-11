import api from '../api/axios';

export async function login(username: string) {
    const response = await api.post('/auth/login', { username });
    return response.data;
}