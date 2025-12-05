<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import {
  VBtn,
  VCard,
  VCardActions,
  VCardText,
  VCardTitle,
  VContainer,
  VDialog,
  VIcon,
  VSelect,
  VSpacer,
  VToolbarTitle,
} from 'vuetify/components';
import { Menu as MenuIcon } from 'lucide-vue-next';
import type { AxiosError } from 'axios';

import ProjectResultsSection from '@/components/organisms/ProjectResultsSection.vue';
import ResultsSection from '@/components/organisms/ResultsSection.vue';
import Sidebar from '@/components/organisms/Sidebar.vue';
import InputSection from '@/components/organisms/InputSection.vue';
import AppShell from '@/components/templates/AppShell.vue';
import { useAuthStore } from '@/stores/auth';
import { useProjectsStore } from '@/stores/projects';
import type { Paper } from '@/types/content';
import { login } from '@/services/auth';
import {
  mapProjectPapers,
  mapSearchResultToPapers,
  performSearch,
  toSidebarProjects,
} from '@/services/papers';

const sidebarOpen = ref(false);
const currentQuery = ref<string | null>(null);
const outputs = ref<Paper[]>([]);
const isProjectView = ref(false);

const errorMessage = ref<string | null>(null);
const isLoading = ref(false);

const authStore = useAuthStore();
const projectsStore = useProjectsStore();

const recentProjects = computed(() => toSidebarProjects(projectsStore.projects));
const projectOptions = computed(() => projectsStore.projects);

onMounted(() => {
  if (authStore.isAuthenticated) {
    projectsStore.loadProjects();
  }
});

const handleSubmitQuery = async (query: string) => {
  currentQuery.value = query;
  isProjectView.value = false;
  outputs.value = [];
  errorMessage.value = null;
  isLoading.value = true;

  try {
    const response = await performSearch(query);
    outputs.value = mapSearchResultToPapers(response);
  } catch (error) {
    console.error('Search failed', error);
    errorMessage.value = 'Suche fehlgeschlagen.';
  } finally {
    isLoading.value = false;
  }
};

const handleProjectSelect = async (projectId: number) => {
  await projectsStore.selectProject(projectId);
  sidebarOpen.value = false;
  const selected = projectsStore.selectedProject;
  if (!selected) return;

  isProjectView.value = true;
  currentQuery.value = selected.project.project_name;
  outputs.value = mapProjectPapers(selected);
};

const handleNewQuery = () => {
  isProjectView.value = false;
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
  const selectedProject = projectsStore.selectedProject;
  if (!selectedProject || !paper.paper_id) {
    return;
  }

  const projectId = selectedProject.project.project_id;
  const paperId = paper.paper_id;

  const previousOutputs = [...outputs.value];
  outputs.value = outputs.value.filter((p) => p.paper_id !== paperId);

  try {
    await projectsStore.removePaper(projectId, paperId);
    outputs.value = mapProjectPapers(projectsStore.selectedProject);
  } catch (err) {
    console.error('Paper removal failed, rolling back', err);

    outputs.value = previousOutputs;
    projectsStore.error = 'Paper konnte nicht entfernt werden.';
  }

  if (outputs.value.length === 0) {
    currentQuery.value = null;
  }
};

const addToProjectDialogOpen = ref(false);
const paperToAdd = ref<Paper | null>(null);
const selectedProjectIdForAdd = ref<number | null>(null);

const handleAddFromSearch = (paper: Paper) => {
  if (!authStore.isAuthenticated || !projectsStore.projects.length) {
    return;
  }
  paperToAdd.value = paper;
  selectedProjectIdForAdd.value = projectsStore.projects[0]?.project_id ?? null;
  addToProjectDialogOpen.value = true;
};

const confirmAddToProject = async () => {
  if (!paperToAdd.value || !paperToAdd.value.paper_id || !selectedProjectIdForAdd.value) {
    addToProjectDialogOpen.value = false;
    return;
  }
  await projectsStore.addPaper(selectedProjectIdForAdd.value, paperToAdd.value.paper_id);
  addToProjectDialogOpen.value = false;
  paperToAdd.value = null;
};
</script>

<template>
  <AppShell :drawer-open="sidebarOpen" @update:drawerOpen="sidebarOpen = $event">
    <template #drawer>
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
    </template>

    <template #app-bar>
      <v-btn icon variant="text" :disabled="isLoading" @click="sidebarOpen = !sidebarOpen">
        <v-icon :icon="MenuIcon" />
      </v-btn>
      <v-toolbar-title class="text-h6">AI Text Processor</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn
        v-if="currentQuery"
        :disabled="isLoading"
        variant="outlined"
        color="primary"
        @click="handleNewQuery"
      >
        Neue Abfrage
      </v-btn>
    </template>

    <v-container fluid class="h-100">
      <div v-if="!currentQuery">
        <InputSection @submit="handleSubmitQuery" />
      </div>
      <div v-else>
        <ProjectResultsSection
          v-if="isProjectView"
          :project-name="currentQuery || ''"
          :papers="outputs"
          :show-abstract="true"
          @remove="handleRemovePaper"
        />
        <ResultsSection
          v-else
          :query="currentQuery"
          :outputs="outputs"
          :show-abstract="true"
          :show-add="authStore.isAuthenticated"
          @add="handleAddFromSearch"
        />
      </div>
    </v-container>

    <template #dialogs>
      <v-dialog v-model="addToProjectDialogOpen" max-width="500">
        <v-card>
          <v-card-title class="text-h5">
            Paper zu Projekt hinzufügen
          </v-card-title>
          <v-card-text>
            <p class="mb-4 text-medium-emphasis">
              Wählen Sie ein Projekt aus, zu dem dieses Paper hinzugefügt werden soll.
            </p>
            <v-select
              v-model="selectedProjectIdForAdd"
              :items="projectOptions"
              item-title="project_name"
              item-value="project_id"
              label="Projekt"
              variant="outlined"
            />
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn variant="text" @click="addToProjectDialogOpen = false">
              Abbrechen
            </v-btn>
            <v-btn color="primary" @click="confirmAddToProject">
              Hinzufügen
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </template>
  </AppShell>
</template>
