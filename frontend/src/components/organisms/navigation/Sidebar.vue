<script setup lang="ts">
  import { ref } from 'vue';
  import {
    VBtn, VCard, VDivider, VIcon, VList, VListItem,
    VListItemTitle
  } from 'vuetify/components';
  import {
    CheckCircle, Clock, FolderOpen, LogIn, LogOut,
    Plus, X, Trash2, Pencil
  } from 'lucide-vue-next';
  import type { Project } from '@/types/content';

  // Import Dialogs
  import LoginDialog from '@/components/dialogs/LoginDialog.vue';
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

  // Dialog State
  const loginDialogOpen = ref(false);
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
            <v-icon :icon="CheckCircle" color="success" class="me-2" size="18" />
            <p class="text-success text-body-2">Successfully logged in</p>
          </div>
        </v-card>
        <v-btn block variant="outlined" color="secondary" @click="emit('logout')">
          <v-icon :icon="LogOut" start size="18" />
          Logout
        </v-btn>
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

  /* 3. Keep visible when menu is open (button is expanded)
     using :has() to check if the child button has aria-expanded="true" */
  .project-action-btn:has(.v-btn[aria-expanded="true"]) {
    opacity: 1;
  }

  .border-b-sm { border-bottom: 1px solid var(--border-sm-color); }
  .border-t-sm { border-top: 1px solid var(--border-sm-color); }
  .bg-green-lighten-5 { background-color: var(--green-lighten-5) !important; }
  .border-success { border: 1px solid var(--border-success) !important; }
</style>