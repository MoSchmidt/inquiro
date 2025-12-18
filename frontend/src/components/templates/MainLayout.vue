<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { VApp, VLayout, VNavigationDrawer, VMain, VSnackbar } from 'vuetify/components'
import { X } from 'lucide-vue-next'
import { useTheme } from 'vuetify'

import AppHeader from '@/components/organisms/layout/AppHeader.vue'
import Sidebar from '@/components/organisms/navigation/Sidebar.vue'
import CreateAccount from '@/components/organisms/auth/CreateAccount.vue'

import { useAuthStore } from '@/stores/auth'
import { useProjectsStore } from '@/stores/projects'
import type { Project } from '@/types/content'

const sidebarOpen = ref(false)
const createAccountOpen = ref(false)

const route = useRoute()
const router = useRouter()
const theme = useTheme()

const authStore = useAuthStore()
const projectsStore = useProjectsStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const projects = computed(() => projectsStore.projects)

onMounted(() => {
  if (isAuthenticated.value) {
    projectsStore.loadProjects()
  }
})

watch(isAuthenticated, (loggedIn) => {
  if (loggedIn) {
    projectsStore.loadProjects()
  } else {
    projectsStore.projects = []
    projectsStore.selectedProject = null
  }
})

const projectLinks = computed<Project[]>(() =>
    projects.value.map((project) => ({
      id: project.project_id,
      name: project.project_name,
      date: project.created_at?.split('T')[0] ?? '',
      outputs: [],
    })),
)

const showNewQuery = computed(() => route.name !== 'search')

const snackbarOpen = ref(false)
const snackbarMessage = ref('')
const snackbarType = ref<'success' | 'error' | 'info'>('success')

const snackbarColor = computed(() => {
  const isDark = theme.global.current.value.dark

  if (snackbarType.value === 'success') {
    return isDark ? '#2E7D32' : 'success'
  }
  return snackbarType.value
})

const showNotification = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
  snackbarMessage.value = message
  snackbarType.value = type
  snackbarOpen.value = true
}

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const goToSearch = () => router.push({ name: 'search' })

const handleNewQuery = () => {
  goToSearch()
  sidebarOpen.value = false
}

const handleProjectSelect = async (projectId: number) => {
  await projectsStore.selectProject(projectId)
  await router.push({ name: 'project', params: { projectId } })
  sidebarOpen.value = false
}

const handleNewProject = async (name: string) => {
  const project = await projectsStore.createNewProject(name)
  if (project) {
    await handleProjectSelect(project.project_id)
  }
}

const handleRenameProject = async (projectId: number, newName: string) => {
  await projectsStore.renameProject(projectId, newName)
}

const handleDeleteProject = async (projectId: number) => {
  await projectsStore.deleteExistingProject(projectId)

  if (route.name === 'project' && Number(route.params.projectId) === projectId) {
    await goToSearch()
    sidebarOpen.value = true
  }
}

const handleLoginSuccess = async () => {
  await projectsStore.loadProjects()
  sidebarOpen.value = true
  showNotification('Successfully logged in!', 'success')
}

const handleLogout = () => {
  authStore.logout()
  projectsStore.projects = []
  projectsStore.selectedProject = null
  handleNewQuery()
  showNotification('Logged out', 'error')
}

const handleAccountCreated = async () => {
  createAccountOpen.value = false
  if (isAuthenticated.value) {
    await projectsStore.loadProjects()
  }
  showNotification('Account created successfully!', 'success')
}
</script>

<template>
  <v-app>
    <v-layout class="h-screen">
      <v-snackbar
          v-model="snackbarOpen"
          :color="snackbarColor"
          location="bottom right"
          timeout="3000"
      >
        {{ snackbarMessage }}

        <template #actions>
          <v-btn
              icon
              variant="text"
              density="compact"
              @click="snackbarOpen = false"
          >
            <v-icon :icon="X" size="18" />
          </v-btn>
        </template>
      </v-snackbar>

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
            @rename-project="handleRenameProject"
            @delete-project="handleDeleteProject"
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

      <v-main class="bg-background scroll-blocked">
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