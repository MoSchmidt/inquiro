import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        accessToken: null,
        refreshToken: null,
        user: null,
    }),

    getters: {
        isAuthenticated: (state) => !!state.accessToken,
    },

    actions: {
        setAuth({ accessToken, refreshToken, user }) {
            this.accessToken = accessToken;
            this.refreshToken = refreshToken;
            this.user = user;
        },

        clearAuth() {
            this.accessToken = null;
            this.refreshToken = null;
            this.user = null;
        },
    },
});
