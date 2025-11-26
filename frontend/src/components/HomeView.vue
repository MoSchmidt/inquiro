<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { VLayout, VAppBar, VNavigationDrawer, VMain, VBtn, VIcon, VToolbarTitle, VContainer } from 'vuetify/components';
import { Menu as MenuIcon } from 'lucide-vue-next';
import Sidebar from './Sidebar.vue';
import InputSection from './InputSection.vue';
import ResultsSection from './ResultsSection.vue';
import type { Paper } from './types';

import { useAuthStore } from '@/stores/auth';
import { useProjectsStore } from '@/stores/projects';
import { login } from '@/services/auth';
import type { AxiosError } from 'axios';

const sidebarOpen = ref(false);
const currentQuery = ref<string | null>(null);
const outputs = ref<Paper[]>([]);

const errorMessage = ref<string | null>(null);
const isLoading = ref(false);

const authStore = useAuthStore();
const projectsStore = useProjectsStore();

const recentProjects = computed(() =>
  projectsStore.projects.map((p) => ({
    id: p.project_id,
    name: p.project_name,
    date: p.created_at.split('T')[0],
    outputs: [] as Paper[],
  })),
);

onMounted(() => {
  if (authStore.isAuthenticated) {
    projectsStore.loadProjects();
  }
});

const handleSubmitQuery = (query: string) => {
  currentQuery.value = query;
  outputs.value = [];
};

const handleProjectSelect = async (projectId: number) => {
  await projectsStore.selectProject(projectId);
  sidebarOpen.value = false;
  const selected = projectsStore.selectedProject;
  if (!selected) return;

  currentQuery.value = selected.project.project_name;
  outputs.value = selected.papers.map((p) => ({
    paper_id: p.paper_id,
    title: p.title,
    author: p.authors ? Object.values(p.authors).join(', ') : '',
    year: p.published_at ? new Date(p.published_at).getFullYear() : 0,
    url: p.url ?? '',
    abstract: p.abstract ?? undefined,
  }));
};

const handleNewQuery = () => {
  currentQuery.value = null;
  outputs.value = [];
};

const handleLogin = async (usernameFromSidebar: string) => {
  isLoading.value = true;
  errorMessage.value = null;

  try {
    const { access_token, refresh_token, user } = await login(usernameFromSidebar);

    authStore.setAuth({
      accessToken: access_token,
      refreshToken: refresh_token,
      user: user,
    });
    await projectsStore.loadProjects();
    sidebarOpen.value = false;
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

const handleLogout = () => {
  authStore.clearAuth();
  projectsStore.$reset();
  currentQuery.value = null;
  outputs.value = [];
};

const handleNewProject = async (name: string) => {
  const project = await projectsStore.createNewProject(name);
  if (project) {
    await handleProjectSelect(project.project_id);
  }
};

const handleRemovePaper = async (paper: Paper) => {
  if (!projectsStore.selectedProject || !paper.paper_id) {
    return;
  }
  await projectsStore.removePaper(projectsStore.selectedProject.project.project_id, paper.paper_id);
  const selected = projectsStore.selectedProject;
  if (!selected) {
    outputs.value = [];
    currentQuery.value = null;
    return;
  }
  outputs.value = selected.papers.map((p) => ({
    paper_id: p.paper_id,
    title: p.title,
    author: p.authors ? Object.values(p.authors).join(', ') : '',
    year: p.published_at ? new Date(p.published_at).getFullYear() : 0,
    url: p.url ?? '',
    abstract: p.abstract ?? undefined,
  }));
};
</script>

<template>
  <v-app>
    <v-layout>
      <v-navigation-drawer
        v-model="sidebarOpen"
        location="left"
        temporary
        width="320"
      >
        <Sidebar
          :is-open="sidebarOpen"
          :recent-projects="recentProjects"
          :is-logged-in="authStore.isAuthenticated"
          @close="sidebarOpen = false"
          @project-select="handleProjectSelect"
          @new-project="handleNewProject"
          @login="handleLogin"
          @logout="handleLogout"
        />
      </v-navigation-drawer>

      <v-app-bar app color="white" flat border>
        <v-btn icon variant="text" @click="sidebarOpen = !sidebarOpen">
          <v-icon :icon="MenuIcon" />
        </v-btn>
        <v-toolbar-title class="text-h6">AI Text Processor</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn v-if="currentQuery" @click="handleNewQuery" variant="outlined" color="primary">
          Neue Abfrage
        </v-btn>
      </v-app-bar>

      <v-main class="bg-grey-lighten-4">
        <v-container fluid class="h-100">
          <div v-if="!currentQuery">
            <InputSection @submit="handleSubmitQuery" />
          </div>
          <div v-else>
            <ResultsSection
              :query="currentQuery"
              :outputs="outputs"
              :show-abstract="true"
              :show-actions="true"
              @remove="handleRemovePaper"
            />
          </div>
        </v-container>
      </v-main>
    </v-layout>
  </v-app>
</template>
<!--<script setup lang="ts">
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
</script>

<template>
  <h1>Hello, {{ authStore.user }}</h1>
  <p>{{ authStore.accessToken }}</p>
</template>

<style scoped></style>-->