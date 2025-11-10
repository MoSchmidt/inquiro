<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const userName = ref('michael');
const errorMessage = ref(null);
const isLoading = ref(false);

const authStore = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  isLoading.value = true;
  errorMessage.value = null;

  try {
    console.log("Trying to login")
    const response = await axios.post('http://localhost:8000/auth/login', {
      user_name: userName.value,
    });
    console.log(response)

    const { access_token, refresh_token, user } = response.data;

    authStore.setAuth({
      accessToken: access_token,
      refreshToken: refresh_token,
      user,
    });

    console.log(authStore.accessToken);

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
    <v-btn @click="handleLogin" :disabled="isLoading || authStore.isAuthenticated">
      {{ isLoading ? 'Logging in...' : 'Login' }}
    </v-btn>
  </div>
</template>
