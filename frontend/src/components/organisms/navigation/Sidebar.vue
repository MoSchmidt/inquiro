<script setup lang="ts">
  import { computed, ref } from 'vue';
  import { useAuthStore } from '@/stores/auth';
  import {
    VBtn,
    VCard,
    VIcon,
    VList,
    VListItem,
  } from 'vuetify/components';
  import {
    FolderOpen,
    LogIn,
    FolderPlus,
    X,
    Trash2,
    Pencil,
    User,
    SquarePen
  } from 'lucide-vue-next';
  import type { Project } from '@/types/content';
  import type { ActionMenuItem } from '@/types/ui'; // Import Shared Type

  // Import Dialogs
  import LoginDialog from '@/components/dialogs/LoginDialog.vue';
  import LogoutDialog from '@/components/dialogs/LogoutDialog.vue';
  import NewProjectDialog from '@/components/dialogs/NewProjectDialog.vue';
  import RenameProjectDialog from '@/components/dialogs/RenameProjectDialog.vue';
  import DeleteProjectDialog from '@/components/dialogs/DeleteProjectDialog.vue';

  import ActionMenu from '@/components/molecules/ActionMenu.vue';

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
    const name = authStore.user?.username || 'User';
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
  <div class="d-flex flex-column h-100 bg-background">

    <v-card
        flat
        color="transparent"
        height="64"
        class="px-4 d-flex align-center justify-space-between"
    >
      <h2 class="text-h6">Menu</h2>
      <v-btn icon variant="text" @click="emit('close')">
        <v-icon :icon="X" size="24" />
      </v-btn>
    </v-card>

    <v-divider />

    <div class="flex-grow-1 overflow-y-auto">
      <div class="px-4 pb-2 pt-4">
        <v-btn
            variant="text"
            color="on-surface"
            rounded="lg"
            block
            height="50"
            class="d-flex justify-start align-center text-none px-4 text-high-emphasis"
            @click="handleNewQueryClick"
        >
          <v-icon :icon="SquarePen" size="20" class="me-3" />
          <span class="font-weight-medium text-body-2">New Query</span>
        </v-btn>
      </div>

      <div class="px-4">
        <h3 class="text-subtitle-1 mb-2 d-flex align-center">
          Projects
        </h3>

        <v-list nav class="pa-0 bg-transparent">
          <v-list-item
              v-for="project in projects"
              :key="project.id"
              @click="emit('projectSelect', project.id)"
              class="rounded-lg project-item px-4"
          >
            <div class="d-flex align-center w-100">
              <v-icon :icon="FolderOpen" size="20" class="me-3" />
              <span class="font-weight-medium text-truncate text-body-2">
                {{ project.name }}
              </span>
            </div>

            <template #append>
              <div class="project-action-btn">
                <ActionMenu :items="getProjectActions(project)" />
              </div>
            </template>
          </v-list-item>

          <v-list-item
              @click="handleNewProjectClick"
              class="rounded-lg project-item px-4"
          >
            <div class="d-flex align-center w-100">
              <v-icon :icon="FolderPlus" size="20" class="me-3" />
              <span class="font-weight-medium text-truncate text-body-2">
                New Project
              </span>
            </div>
          </v-list-item>
        </v-list>
      </div>
    </div>

    <div class="px-4 py-2">
      <h3 class="text-subtitle-1 mb-2 d-flex align-center">Account</h3>
      <div v-if="!isLoggedIn">
        <v-btn
            variant="text"
            color="on-surface"
            rounded="lg"
            block
            height="50"
            class="d-flex justify-start align-center text-none px-4 text-high-emphasis"
            @click="loginDialogOpen = true"
        >
          <v-icon :icon="LogIn" size="20" class="me-3" />
          <span class="font-weight-medium text-body-2">Login</span>
        </v-btn>
      </div>

      <div v-else>
        <v-btn
            variant="text"
            color="on-surface"
            rounded="lg"
            block
            height="50"
            class="d-flex justify-start align-center text-none px-4 text-high-emphasis"
            @click="logoutDialogOpen = true"
        >
          <v-icon :icon="User" size="20" class="me-3" />
          <span class="font-weight-medium text-body-2">{{ formattedUsername }}</span>
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
    <LogoutDialog
        v-model="logoutDialogOpen"
        @logout="onLogoutConfirm"
    />
  </div>
</template>

<style scoped>
  /* --- Action Button Opacity Logic --- */
  .project-action-btn {
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
    display: flex;
    align-items: center;
  }

  .project-item:hover .project-action-btn,
  .project-item:focus-within .project-action-btn {
    opacity: 1;
  }

  .project-item {
    min-height: 50px !important;
  }
</style>