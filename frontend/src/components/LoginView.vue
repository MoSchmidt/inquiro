<script setup lang="ts">
import { ref } from 'vue';
import { AxiosError } from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { login } from '@/services/auth';

const username = ref('');
const errorMessage = ref<string | null>(null);
const isLoading = ref(false);

const authStore = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  isLoading.value = true;
  errorMessage.value = null;

  try {
    const { access_token, refresh_token, user } = await login(username.value);

    authStore.setAuth({
      accessToken: access_token,
      refreshToken: refresh_token,
      user: user,
    });

    await router.push({ name: 'home' });
  } catch (error: unknown) {
    const axiosError = error as AxiosError<{ detail?: string }>;

    if (axiosError.response?.data?.detail) {
      errorMessage.value = axiosError.response.data.detail;
    } else {
      errorMessage.value = 'An unexpected error occurred.';
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <v-container fluid>
    <v-card class="mx-auto" max-width="420">
      <v-card-title> Login </v-card-title>

      <v-card-text>
        <v-alert
          v-if="errorMessage"
          type="error"
          variant="tonal"
          density="compact"
          class="mb-4"
        >
          {{ errorMessage }}
        </v-alert>

        <v-text-field
          v-model="username"
          label="Username"
          variant="outlined"
          density="comfortable"
        />
      </v-card-text>

      <v-card-actions>
        <v-btn
          color="primary"
          block
          :disabled="isLoading || authStore.isAuthenticated"
          @click="handleLogin"
        >
          Sign in
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>
