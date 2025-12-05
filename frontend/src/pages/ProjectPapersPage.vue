<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  VAlert,
  VBtn,
  VCard,
  VCardText,
  VContainer,
  VIcon,
  VSpacer,
  VToolbarTitle,
} from 'vuetify/components';
import { FileText, Menu as MenuIcon, Trash2 } from 'lucide-vue-next';
import type { AxiosError } from 'axios';

import PaperList from '@/components/molecules/PaperList.vue';
import Sidebar from '@/components/organisms/Sidebar.vue';
import AppShell from '@/components/templates/AppShell.vue';
import { useAuthStore } from '@/stores/auth';
import { useProjectsStore } from '@/stores/projects';
import type { Paper, PaperMenuOption } from '@/types/content';
import { login } from '@/services/auth';
import { mapProjectPapers, toSidebarProjects } from '@/services/papers';

const route = useRoute();
const router = useRouter();
const sidebarOpen = ref(false);
const errorMessage = ref<string | null>(null);
const isLoading = ref(false);
const outputs = ref<Paper[]>([]);

const authStore = useAuthStore();
const projectsStore = useProjectsStore();

const currentProjectId = computed(() => Number(route.params.projectId));
const projectName = computed(() => projectsStore.selectedProject?.project.project_name ?? '');
const recentProjects = computed(() => toSidebarProjects(projectsStore.projects));

const menuOptions: PaperMenuOption[] = [
  { label: 'Remove from Project', value: 'remove', icon: Trash2 },
];

const loadProject = async (projectId: number) => {
  if (!projectId) return;
  isLoading.value = true;
  errorMessage.value = null;
  outputs.value = [];

  try {
    if (authStore.isAuthenticated && !projectsStore.projects.length) {
      await projectsStore.loadProjects();
    }
    await projectsStore.selectProject(projectId);
    if (!projectsStore.selectedProject) {
      errorMessage.value = 'Projekt konnte nicht geladen werden.';
      return;
    }
    outputs.value = mapProjectPapers(projectsStore.selectedProject);
  } catch (error) {
    console.error('Failed to load project papers', error);
    errorMessage.value = 'Projekt konnte nicht geladen werden.';
  } finally {
    isLoading.value = false;
  }
};

onMounted(async () => {
  if (authStore.isAuthenticated && !projectsStore.projects.length) {
    await projectsStore.loadProjects();
  }
  await loadProject(currentProjectId.value);
});

watch(
  () => route.params.projectId,
  async (newId) => {
    if (newId) {
      await loadProject(Number(newId));
    }
  },
);

const handleProjectSelect = async (projectId: number) => {
  sidebarOpen.value = false;
  await router.push({ name: 'project-papers', params: { projectId } });
};

const handleNewProject = async (name: string) => {
  const project = await projectsStore.createNewProject(name);
  if (project) {
    await router.push({ name: 'project-papers', params: { projectId: project.project_id } });
  }
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
  outputs.value = [];
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
};

const handleMenuSelect = ({ option, paper }: { option: PaperMenuOption; paper: Paper }) => {
  switch (option.value) {
    case 'remove':
      handleRemovePaper(paper);
      break;
  }
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
      <v-toolbar-title class="text-h6">Projektbibliothek</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn variant="outlined" color="primary" :disabled="isLoading" @click="router.push('/')">
        Neue Abfrage
      </v-btn>
    </template>

    <v-container class="py-6" style="max-width: 1200px;">
      <v-alert v-if="errorMessage" type="error" variant="tonal" class="mb-4">
        {{ errorMessage }}
      </v-alert>
      <v-card flat class="mb-6 pa-4 project-header-card">
        <v-card-text class="pa-0">
          <div class="d-flex align-center mb-2">
            <div class="project-icon d-flex align-center justify-center me-3">
              <v-icon :icon="FileText" size="20" />
            </div>
            <h1 class="project-title">
              {{ projectName }}
            </h1>
          </div>
          <p class="text-caption text-medium-emphasis">
            {{ outputs.length }} gespeicherte Paper
          </p>
        </v-card-text>
      </v-card>

      <PaperList
        :papers="outputs"
        :show-abstract="true"
        :show-add="false"
        :menu-options="menuOptions"
        title="Artikel"
        empty-message="Dieses Projekt hat noch keine gespeicherten Paper."
        :expand-all-on-change="false"
        @menu-select="handleMenuSelect"
      />
    </v-container>
  </AppShell>
</template>

<style scoped>
.project-header-card {
  border-radius: 0;
  border: none;
  border-bottom: 1px solid rgba(148, 163, 184, 0.45);
  background: transparent;
}

.project-icon {
  width: 40px;
  height: 40px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.04);
  color: #1f2937;
}

.project-title {
  font-size: 1.8rem;
  font-weight: 650;
  letter-spacing: 0.02em;
}
</style>
