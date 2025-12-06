<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { RouterView, useRoute, useRouter } from 'vue-router';
import { VApp, VLayout, VNavigationDrawer, VMain } from 'vuetify/components';
import AppHeader from '@/components/organisms/layout/AppHeader.vue';
import Sidebar from '@/components/organisms/navigation/Sidebar.vue';
import CreateAccount from '@/components/organisms/auth/CreateAccount.vue';
import { useAuthService } from '@/services/authService';
import { useProjectsService } from '@/services/projectsService';
import type { Project } from '@/types/content';

const sidebarOpen = ref(false);
const createAccountOpen = ref(false);

const route = useRoute();
const router = useRouter();

const { isAuthenticated, logoutUser } = useAuthService();
const { projects, loadProjects, selectProject, createProject, resetProjects } = useProjectsService();

onMounted(() => {
  if (isAuthenticated.value) {
    loadProjects();
  }
});

watch(isAuthenticated, (loggedIn) => {
  if (loggedIn) {
    loadProjects();
  } else {
    resetProjects();
  }
});

const projectLinks = computed<Project[]>(() =>
  projects.value.map((project) => ({
    id: project.project_id,
    name: project.project_name,
    date: project.created_at?.split('T')[0] ?? '',
    outputs: [],
  })),
);

const showNewQuery = computed(() => route.name !== 'search');

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value;
};

const goToSearch = () => router.push({ name: 'search' });

const handleNewQuery = () => {
  goToSearch();
  sidebarOpen.value = false;
};

const handleProjectSelect = async (projectId: number) => {
  await selectProject(projectId);
  await router.push({ name: 'project', params: { projectId } });
  sidebarOpen.value = false;
};

const handleNewProject = async (name: string) => {
  const project = await createProject(name);
  if (project) {
    await handleProjectSelect(project.project_id);
  }
};

const handleLoginSuccess = async () => {
  await loadProjects();
  sidebarOpen.value = true;
};

const handleLogout = () => {
  logoutUser();
  resetProjects();
  handleNewQuery();
};

const handleAccountCreated = async () => {
  createAccountOpen.value = false;
  if (isAuthenticated.value) {
    await loadProjects();
  }
};
</script>

<template>
  <v-app>
    <v-layout class="h-screen">
      <v-navigation-drawer
        v-model="sidebarOpen"
        location="left"
        temporary
        width="320"
        app
      >
        <Sidebar
          :is-open="sidebarOpen"
          :projects="projectLinks"
          :is-logged-in="isAuthenticated"
          @close="sidebarOpen = false"
          @project-select="handleProjectSelect"
          @new-project="handleNewProject"
          @logout="handleLogout"
          @new-query="handleNewQuery"
          @login-success="handleLoginSuccess"
        />
      </v-navigation-drawer>

      <AppHeader
        :is-authenticated="isAuthenticated"
        :show-new-query="showNewQuery"
        @toggle-sidebar="toggleSidebar"
        @new-query="handleNewQuery"
        @open-create-account="createAccountOpen = true"
      />

      <v-main class="bg-grey-lighten-4 scroll-blocked">
        <div class="scroll-container">
          <RouterView />
        </div>
      </v-main>

      <CreateAccount
        :open="createAccountOpen"
        @close="createAccountOpen = false"
        @create="handleAccountCreated"
      />
    </v-layout>
  </v-app>
</template>

<style scoped>
.scroll-blocked {
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.scroll-container {
  flex: 1 1 auto;
  height: 100%;
  overflow-y: auto;
  padding: 16px;
}
</style>
