<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { login } from '@/services/auth';
import {
  VList,
  VListItem,
  VDivider,
  VBtn,
  VIcon,
  VCard,
  VTextField,
  VDialog,
  VCardActions,
  VCardText,
  VCardTitle,
} from 'vuetify/components';
import { X, LogOut, FolderOpen, Clock, LogIn, Plus, CheckCircle } from 'lucide-vue-next';
import type { Project } from './types';

const props = defineProps<{
  isOpen: boolean;
  recentProjects: Project[];
  isLoggedIn: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'projectSelect', projectId: number): void;
  (e: 'newProject', name: string): void;
  (e: 'login', username: string): void;
  (e: 'logout'): void;
}>();

const username = ref('');
const loginDialogOpen = ref(false);
const loginError = ref<string | null>(null);
const loginLoading = ref(false);
const authStore = useAuthStore();
const newProjectDialogOpen = ref(false);
const newProjectName = ref('');

const handleLoginSubmit = async () => {
  loginError.value = null;
  if (!username.value) return;

  loginLoading.value = true;
  try {
    const resp = await login(username.value);
    if (resp && resp.access_token) {
      authStore.setAuth({
        accessToken: resp.access_token,
        refreshToken: resp.refresh_token,
        user: resp.user,
      });
      // close dialog and notify parent
      username.value = '';
      loginDialogOpen.value = false;
      emit('login', username.value);
      emit('close');
    } else {
      loginError.value = 'Login failed';
    }
  } catch (err: unknown) {
    // try to read axios error message
    try {
      // @ts-ignore
      const message = err?.response?.data?.detail || err?.message;
      loginError.value = message ?? 'Login failed';
    } catch {
      loginError.value = 'Login failed';
    }
  } finally {
    loginLoading.value = false;
  }
};

const handleNewProjectClick = () => {
  if (!props.isLoggedIn) {
    loginDialogOpen.value = true;
    return;
  }
  newProjectDialogOpen.value = true;
};

const handleNewProjectSubmit = () => {
  if (!newProjectName.value) return;
  emit('newProject', newProjectName.value);
  newProjectName.value = '';
  newProjectDialogOpen.value = false;
  emit('close');
};
</script>

<template>
  <div class="d-flex flex-column h-100">
    <v-card flat class="pa-4 d-flex align-center justify-space-between border-b-sm">
      <h2 class="text-h6">Menu</h2>
      <v-btn icon variant="text" @click="emit('close')">
        <v-icon :icon="X" size="24" />
      </v-btn>
    </v-card>

    <div class="flex-grow-1 overflow-y-auto">
      <div class="pa-4 pb-2">
        <v-btn
          color="secondary"
          variant="outlined"
          block
          @click="handleNewProjectClick"
        >
          <v-icon :icon="Plus" start size="18" />
          New Project
        </v-btn>
      </div>

      <v-divider class="my-3" />

      <div class="px-4">
        <h3 class="text-subtitle-1 mb-3 d-flex align-center">
          <v-icon :icon="Clock" size="16" class="me-2" />
          Your Projects
        </h3>
        <v-list density="compact" nav class="pa-0">
          <v-list-item
            v-for="project in recentProjects"
            :key="project.id"
            @click="emit('projectSelect', project.id)"
            class="mb-2 rounded-lg"
            :title="project.name"
            lines="three"
          >
            <template #prepend>
              <v-icon :icon="FolderOpen" color="blue-darken-2"></v-icon>
            </template>
            <template #append>
              <span class="text-caption text-medium-emphasis me-2">
                {{ project.date }}
              </span>
            </template>
          </v-list-item>
        </v-list>
      </div>
    </div>

    <div class="border-t-sm pa-4">
      <h3 class="text-subtitle-1 mb-3 d-flex align-center">
        Account
      </h3>
      <div v-if="!isLoggedIn">
        <v-btn block color="primary" @click="loginDialogOpen = true">
          <v-icon :icon="LogIn" start size="18" />
          Login
        </v-btn>
      </div>
      <div v-else>
        <v-card flat class="pa-3 mb-3 bg-green-lighten-5 border-success">
          <div class="d-flex align-center">
            <v-icon :icon="CheckCircle" color="success" class="me-2" size="18"></v-icon>
            <p class="text-success text-body-2">Successfully logged in</p>
          </div>
        </v-card>
        <v-btn block variant="outlined" color="secondary" @click="emit('logout')">
          <v-icon :icon="LogOut" start size="18" />
          Logout
        </v-btn>
      </div>
    </div>

    <v-dialog v-model="loginDialogOpen" max-width="500">
      <v-card>
        <v-card-title class="text-h5">Login to your account</v-card-title>
        <v-card-text>
          <p class="mb-4 text-medium-emphasis">
            Enter your username to access your projects.
          </p>
          <v-form @submit.prevent="handleLoginSubmit">
            <v-text-field
              v-model="username"
              label="Username"
              type="text"
              variant="outlined"
              required
              class="mb-4"
            ></v-text-field>
            <v-btn type="submit" color="primary" block>Login</v-btn>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" variant="text" @click="loginDialogOpen = false">
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="newProjectDialogOpen" max-width="500">
      <v-card>
        <v-card-title class="text-h5">New Project</v-card-title>
        <v-card-text>
          <p class="mb-4 text-medium-emphasis">
            Enter a name for your new project.
          </p>
          <v-form @submit.prevent="handleNewProjectSubmit">
            <v-text-field
              v-model="newProjectName"
              label="Project name"
              type="text"
              variant="outlined"
              required
              class="mb-4"
            ></v-text-field>
            <v-btn type="submit" color="primary" block>Create Project</v-btn>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" variant="text" @click="newProjectDialogOpen = false">
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
.border-b-sm {
  border-bottom: 1px solid #E0E0E0;
}
.border-t-sm {
  border-top: 1px solid #E0E0E0;
}
.bg-green-lighten-5 {
  background-color: #F1F8E9 !important;
}
.border-success {
  border: 1px solid #8BC34A !important;
}
</style>