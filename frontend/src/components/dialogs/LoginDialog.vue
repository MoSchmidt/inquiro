<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import {
  VDialog, VCard, VCardTitle, VCardText, VCardActions,
  VForm, VTextField, VBtn, VSpacer
} from 'vuetify/components';

const props = defineProps<{
  modelValue: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'success'): void;
}>();

const { login } = useAuthStore();

const username = ref('');
const password = ref('');
const loading = ref(false);
const error = ref<string | null>(null);

const close = () => {
  emit('update:modelValue', false);
  // Optional: Reset fields on close
  username.value = '';
  password.value = '';
  error.value = null;
};

const handleSubmit = async () => {
  error.value = null;
  if (!username.value || !password.value) {
    error.value = 'Username and password are required';
    return;
  }

  loading.value = true;
  try {
    await login(username.value, password.value);
    // Reset form
    username.value = '';
    password.value = '';
    emit('success');
    close();
  } catch (err: any) {
    // Error handling logic
    const message = err?.response?.data?.detail || err?.message;
    error.value = message ?? 'Login failed';
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <v-dialog :model-value="modelValue" @update:model-value="close" max-width="500">
    <v-card>
      <v-card-title class="text-h6 pa-4 pb-0">Login to your account</v-card-title>
      <v-card-text class="pa-4">
        <p class="mb-4 text-medium-emphasis text-body-2">
          Enter your username and password to access your projects.
        </p>
        <v-form @submit.prevent="handleSubmit">
          <v-text-field v-model="username" label="Username" variant="outlined" required class="mb-2" />
          <v-text-field v-model="password" label="Password" type="password" variant="outlined" required />
          <div v-if="error" class="mt-2 text-caption text-error">{{ error }}</div>
        </v-form>
      </v-card-text>

      <v-card-actions class="pa-4 pt-0">
        <v-spacer />
        <v-btn variant="text" class="text-medium-emphasis text-none" @click="close">Cancel</v-btn>
        <v-btn
            color="secondary"
            variant="text"
            class="text-none"
            :loading="loading"
            @click="handleSubmit"
        >
          Login
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.text-error {
  color: rgb(var(--v-theme-error));
}
</style>
