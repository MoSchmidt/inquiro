<script setup lang="ts">
  import {computed, ref} from 'vue';
  import { useAuthStore } from '@/stores/auth';
  import {
    VBtn, VCard, VDivider, VIcon, VList, VListItem,
    VListItemTitle
  } from 'vuetify/components';
  import {
    Clock, FolderOpen, FolderPlus, LogIn,
    Plus, X, Trash2, Pencil, User
  } from 'lucide-vue-next';
  import type { Project } from '@/types/content';

  // Import Dialogs
  import LoginDialog from '@/components/dialogs/LoginDialog.vue';
  import LogoutDialog from '@/components/dialogs/LogoutDialog.vue';
  import NewProjectDialog from '@/components/dialogs/NewProjectDialog.vue';
  import RenameProjectDialog from '@/components/dialogs/RenameProjectDialog.vue';
  import DeleteProjectDialog from '@/components/dialogs/DeleteProjectDialog.vue';

  import ActionMenu, { type ActionMenuItem } from '@/components/molecules/ActionMenu.vue';

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
    (e: 'deleteProject', projectId: number): void;
    (e: 'renameProject', projectId: number, newName: string): void;
  }>();

  const authStore = useAuthStore();

  const formattedUsername = computed(() => {
    // Get username from store (fallback to 'User' if empty)
    const name = authStore.user?.username || 'User';

    if (!name) return '';

    // Uppercase the first letter and concatenate the rest
    return name.charAt(0).toUpperCase() + name.slice(1);
  });

  // Dialog State
  const loginDialogOpen = ref(false);
  const logoutDialogOpen = ref(false);
  const newProjectDialogOpen = ref(false);
  const renameDialogOpen = ref(false);
  const deleteDialogOpen = ref(false);

  const projectToAction = ref<Project | null>(null);

  // Actions
  const openRenameDialog = (project: Project) => {
    projectToAction.value = project;
    renameDialogOpen.value = true;
  };

  const openDeleteDialog = (project: Project) => {
    projectToAction.value = project;
    deleteDialogOpen.value = true;
  };

  // Helper to generate menu items for a specific project
  const getProjectActions = (project: Project): ActionMenuItem[] => [
    {
      title: 'Rename',
      value: 'rename',
      icon: Pencil,
      action: () => openRenameDialog(project)
    },
    {
      title: 'Delete',
      value: 'delete',
      color: 'error',
      icon: Trash2,
      action: () => openDeleteDialog(project)
    }
  ];

  const handleNewProjectClick = () => {
    if (!props.isLoggedIn) {
      loginDialogOpen.value = true;
      return;
    }
    newProjectDialogOpen.value = true;
  };

  const onNewProjectSubmit = (name: string) => {
    emit('newProject', name);
    emit('close');
  };

  const onLoginSuccess = () => {
    emit('loginSuccess');
    emit('close');
  };

  const onRenameSubmit = (newName: string) => {
    if (projectToAction.value) {
      emit('renameProject', projectToAction.value.id, newName);
    }
  };

  const onDeleteSubmit = () => {
    if (projectToAction.value) {
      emit('deleteProject', projectToAction.value.id);
    }
  };

  const handleNewQueryClick = () => {
    emit('newQuery');
    emit('close');
  };

  const onLogoutConfirm = () => {
    emit('logout');
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
            class="aligned-button"
            @click="handleNewQueryClick"
        >
          <v-icon :icon="Plus" start size="18" />
          New Query
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
              class="mb-2 rounded-lg project-item"
          >
            <template #prepend>
              <v-icon :icon="FolderOpen" color="blue-darken-2" class="me-1" />
            </template>

            <v-list-item-title class="font-weight-medium">
              {{ project.name }}
            </v-list-item-title>

            <template #append>
              <div class="project-action-btn">
                <ActionMenu :items="getProjectActions(project)" />
              </div>
            </template>
          </v-list-item>

          <v-list-item
              @click="handleNewProjectClick"
              class="mb-2 rounded-lg project-item"
          >
            <template #prepend>
              <v-icon :icon="FolderPlus" color="blue-darken-2" class="me-1" />
            </template>

            <v-list-item-title class="font-weight-medium">
              New Project
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </div>
    </div>

    <div class="border-t-sm pa-4">
      <div v-if="!isLoggedIn">
        <v-btn block color="primary" @click="loginDialogOpen = true">
          <v-icon :icon="LogIn" start size="18" />
          Login
        </v-btn>
      </div>

      <div v-else>
        <v-list density="compact" nav class="pa-0">
          <v-list-item
              @click="logoutDialogOpen = true"
              class="rounded-lg project-item"
          >
            <template #prepend>
              <v-icon :icon="User" class="me-1" />
            </template>

            <v-list-item-title class="font-weight-medium">
              {{ formattedUsername }}
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </div>
    </div>

    <LoginDialog v-model="loginDialogOpen" @success="onLoginSuccess" />
    <NewProjectDialog v-model="newProjectDialogOpen" @submit="onNewProjectSubmit" />
    <RenameProjectDialog
        v-model="renameDialogOpen"
        :current-name="projectToAction?.name || ''"
        @submit="onRenameSubmit"
    />
    <DeleteProjectDialog
        v-model="deleteDialogOpen"
        :project-name="projectToAction?.name || ''"
        @submit="onDeleteSubmit"
    />

    <LogoutDialog
        v-model="logoutDialogOpen"
        @logout="onLogoutConfirm"
    />
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

  /* --- Action Button Opacity Logic --- */

  /* 1. Hide by default */
  .project-action-btn {
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
    /* Ensure the wrapper doesn't collapse */
    display: flex;
    align-items: center;
  }

  /* 2. Show when hovering over the row (.project-item) */
  .project-item:hover .project-action-btn,
  .project-item:focus-within .project-action-btn {
    opacity: 1;
  }

  /* Ensure minimum height for project items */
  .project-item {
    min-height: 50px !important;
  }

  .border-b-sm { border-bottom: 1px solid var(--border-sm-color); }
  .border-t-sm { border-top: 1px solid var(--border-sm-color); }
</style>