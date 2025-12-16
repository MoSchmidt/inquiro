<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import {
  VDialog, VCard, VCardTitle, VCardText, VCardActions,
  VForm, VTextField, VBtn, VSpacer
} from 'vuetify/components'
import type { AxiosError } from 'axios';

const props = defineProps<{ open: boolean }>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'create', payload: { name: string; email: string; password: string }): void
}>()

const dialogOpen = computed({
  get: () => props.open,
  set: (value: boolean) => {
    if (!value) emit('close')
  },
})


const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref<string | null>(null)
const loading = ref(false)

const authStore = useAuthStore()


const resetForm = () => {
  name.value = ''
  email.value = ''
  password.value = ''
  confirmPassword.value = ''
  error.value = null
}


const submit = async () => {
  error.value = null

  // UI-level validation
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  if (password.value.length < 8) {
    error.value = 'Password must be at least 8 characters long'
    return
  }

  loading.value = true

  try {
    const username = name.value
    await authStore.signup(username, password.value)

    emit('create', {
      name: name.value,
      email: email.value,
      password: password.value,
    })

    resetForm()
    dialogOpen.value = false
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as AxiosError<{ detail?: string }>;
      error.value = axiosErr.response?.data?.detail ||
        axiosErr.message ||
        'Signup failed';
    } else {
      error.value = (err as Error)?.message || 'Signup failed';
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <v-dialog v-model="dialogOpen" max-width="500">
    <v-card>
      <v-card-title class="text-h5">Create Account</v-card-title>
      <v-card-text>
        <p class="mb-4 text-medium-emphasis">
          Create an account to save your research projects.
        </p>

        <v-form @submit.prevent="submit">
          <v-text-field
            v-model="name"
            label="Username"
            variant="outlined"
            class="mb-3"
            autofocus
          />

          <v-text-field
            v-model="email"
            label="Email (optional)"
            type="email"
            variant="outlined"
            class="mb-3"
          />

          <v-text-field
            v-model="password"
            label="Password"
            type="password"
            variant="outlined"
            class="mb-3"
          />

          <v-text-field
            v-model="confirmPassword"
            label="Confirm Password"
            type="password"
            variant="outlined"
            class="mb-4"
          />

          <div v-if="error" class="mb-4 text-error text-body-2">
            {{ error }}
          </div>

          <v-btn
            type="submit"
            color="primary"
            block
            :loading="loading"
          >
            Sign Up
          </v-btn>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="dialogOpen = false">
          Cancel
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
