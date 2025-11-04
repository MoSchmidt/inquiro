<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const username = ref('michael');
const errorMessage = ref(null);
const isLoading = ref(false);

const authStore = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  isLoading.value = true;
  errorMessage.value = null;

  try {
    const response = await axios.post('http://localhost:8000/auth/login', {
      username: username.value,
    });

    const { access_token, refresh_token, user } = response.data;

    authStore.setAuth({
      accessToken: access_token,
      refreshToken: refresh_token,
      user,
    });

    await router.push({ name: 'home' });

  } catch (error) {
    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail;
    } else {
      errorMessage.value = 'An unexpected error occurred.';
    }
    console.error('Login failed:', error);
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div>
    <v-btn @click="handleLogin" :disabled="isLoading || authStore.isLoggedIn">
      {{ isLoading ? 'Logging in...' : 'Login' }}
    </v-btn>

    <v-btn v-if="authStore.isLoggedIn" color="error" @click="authStore.logout">
      Logout
    </v-btn>

    <p v-if="authStore.isLoggedIn" class="text-green-600">
      ✅ Logged in as: {{ authStore.user?.username }}
    </p>
    <p v-else class="text-gray-600">🔒 Not logged in</p>
  </div>
</template>
