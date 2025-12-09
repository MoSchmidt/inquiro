<script setup lang="ts">
import { ref } from 'vue';
import {
  VBtn,
  VCard,
  VCardActions,
  VCardText,
  VCardTitle,
  VDialog,
  VDivider,
  VIcon,
  VList,
  VListItem,
  VTextField,
} from 'vuetify/components';
import {
  CheckCircle,
  Clock,
  FolderOpen,
  LogIn,
  LogOut,
  Plus,
  X,
} from 'lucide-vue-next';
import type { Project } from '@/types/content';
import { useAuthStore } from '@/stores/auth';

const props = defineProps<{
  isOpen: boolean;
  projects: Project[];
  isLoggedIn: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'projectSelect', projectId: number): void;
  (e: 'newProject', name: string): void;
  (e: 'logout'): void;
  (e: 'newQuery'): void;
  (e: 'loginSuccess'): void;
}>();

const username = ref('');
const password = ref('');
const loginDialogOpen = ref(false);
const loginError = ref<string | null>(null);
const loginLoading = ref(false);
const newProjectDialogOpen = ref(false);
const newProjectName = ref('');
const { login } = useAuthStore();

const handleNewQueryClick = () => {
  emit('newQuery');
  emit('close');
};
const handleLoginSubmit = async () => {
  loginError.value = null;
  if (!username.value || !password.value) {
    loginError.value = 'Username and password are required';
    return;
  }

  loginLoading.value = true;
  try {
    await login(username.value, password.value);
    emit('loginSuccess');
    username.value = '';
    password.value = '';
    loginDialogOpen.value = false;
    emit('close');
  } catch (err: unknown) {
    try {
      // @ts-expect-error
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
    <v-card
      flat
      class="pa-4 d-flex align-center justify-space-between border-b-sm"
    >
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
          class="aligned-button"
          @click="handleNewQueryClick"
        >
          <v-icon :icon="Plus" start size="18" />
          New Query
        </v-btn>
      </div>

      <div class="pa-4 pb-2">
        <v-btn
          color="secondary"
          variant="outlined"
          block
          class="aligned-button"
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
            v-for="project in projects"
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
      <h3 class="text-subtitle-1 mb-3 d-flex align-center">Account</h3>
      <div v-if="!isLoggedIn">
        <v-btn block color="primary" @click="loginDialogOpen = true">
          <v-icon :icon="LogIn" start size="18" />
          Login
        </v-btn>
      </div>
      <div v-else>
        <v-card flat class="pa-3 mb-3 bg-green-lighten-5 border-success">
          <div class="d-flex align-center">
            <v-icon
              :icon="CheckCircle"
              color="success"
              class="me-2"
              size="18"
            ></v-icon>
            <p class="text-success text-body-2">Successfully logged in</p>
          </div>
        </v-card>
        <v-btn
          block
          variant="outlined"
          color="secondary"
          @click="emit('logout')"
        >
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
            <v-text-field
              v-model="password"
              label="Password"
              type="password"
              variant="outlined"
              required
              class="mb-4"
            ></v-text-field>
            <v-btn type="submit" color="primary" block :loading="loginLoading"
              >Login</v-btn
            >
            <div
              v-if="loginError"
              class="mt-2"
              style="color: var(--v-theme-error)"
            >
              {{ loginError }}
            </div>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="secondary"
            variant="text"
            @click="loginDialogOpen = false"
          >
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
          <v-btn
            color="secondary"
            variant="text"
            @click="newProjectDialogOpen = false"
          >
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
.aligned-button {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  text-align: left;
}

.border-b-sm {
  border-bottom: 1px solid var(--border-sm-color);
}
.border-t-sm {
  border-top: 1px solid var(--border-sm-color);
}
.bg-green-lighten-5 {
  background-color: var(--green-lighten-5) !important;
}
.border-success {
  border: 1px solid var(--border-sucess) !important;
}
</style>
