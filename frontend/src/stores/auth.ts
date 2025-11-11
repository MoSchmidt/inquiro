import { defineStore } from 'pinia';

interface ApiUser {
    user_id: number;
    username: string;
}

interface User {
    id: number;
    username: string;
}

interface AuthState {
    accessToken: string | null;
    refreshToken: string | null;
    user: User | null;
}

export const useAuthStore = defineStore('auth', {
    state: (): AuthState => ({
        accessToken: null,
        refreshToken: null,
        user: null,
    }),

    getters: {
        isAuthenticated: (state) => !!state.accessToken,
    },

    actions: {
        setAuth(payload: { accessToken: string, refreshToken: string, user: ApiUser }) {
            const { accessToken, refreshToken, user } = payload;
            this.accessToken = accessToken;
            this.refreshToken = refreshToken;
            this.user = {
                id: user.user_id,
                username: user.username,
            };
        },

        clearAuth() {
            this.accessToken = null;
            this.refreshToken = null;
            this.user = null;
        },
    },
});
