<script setup lang="ts">
import { ref } from 'vue';
import PaperList from '@/components/PaperList.vue';
import {
  VCard,
  VCardText,
  VIcon,
  VBtn,
  VContainer,
  VDialog,
  VTextField,
  VCardActions,
  VSpacer,
  VTooltip
} from 'vuetify/components';
import { FileText, Trash2, Pencil } from 'lucide-vue-next';
import type { Paper, PaperMenuOption } from './types';

const props = defineProps<{
  projectName: string;
  papers: Paper[];
  showAbstract?: boolean;
}>();

const emit = defineEmits<{
  (e: 'remove', paper: Paper): void;
  (e: 'rename', newName: string): void;
}>();

const isRenameDialogOpen = ref(false);
const tempNewName = ref('');

const openRenameDialog = () => {
  tempNewName.value = props.projectName;
  isRenameDialogOpen.value = true;
};

const saveRename = () => {
  const trimmedName = tempNewName.value.trim();
  if (trimmedName) {
    emit('rename', trimmedName);
    isRenameDialogOpen.value = false;
  }
};


const menuOptions: PaperMenuOption[] = [
  { label: 'Remove from Project', value: 'remove', icon: Trash2 },
];

const handleMenuSelect = ({
  option,
  paper,
}: {
  option: PaperMenuOption;
  paper: Paper;
}) => {
  switch (option.value) {
    case 'remove':
      emit('remove', paper);
      break;
  }
};
</script>

<template>
  <v-container class="py-6" style="max-width: 1200px;">
    <v-card flat class="mb-6 pa-4 project-header-card">
      <v-card-text class="pa-0">
        <div class="d-flex align-center mb-2">
          <div class="project-icon d-flex align-center justify-center me-3">
            <v-icon :icon="FileText" size="20" />
          </div>

          <h1 class="project-title me-3">
            {{ projectName }}
          </h1>

          <v-btn
              icon
              variant="text"
              size="small"
              color="medium-emphasis"
              @click="openRenameDialog"
          >
            <v-icon :icon="Pencil" size="20" />
            <v-tooltip activator="parent" location="top">
              Rename project
            </v-tooltip>
          </v-btn>
        </div>
        <p class="text-caption text-medium-emphasis">
          {{ papers.length }} gespeicherte Paper
        </p>
      </v-card-text>
    </v-card>

    <PaperList
      :papers="papers"
      :show-abstract="showAbstract"
      :show-add="false"
      :menu-options="menuOptions"
      title="Artikel"
      empty-message="Dieses Projekt hat noch keine gespeicherten Paper."
      :expand-all-on-change="false"
      @menu-select="handleMenuSelect"
    />
    <v-dialog v-model="isRenameDialogOpen" max-width="500">
      <v-card class="pa-4">
        <h3 class="text-h6 mb-4">Rename Project</h3>

        <v-text-field
            v-model="tempNewName"
            label="Project Name"
            variant="outlined"
            autofocus
            @keyup.enter="saveRename"
        ></v-text-field>

        <v-card-actions class="px-0">
          <v-spacer></v-spacer>
          <v-btn
              variant="text"
              color="grey-darken-1"
              @click="isRenameDialogOpen = false"
          >
            Cancel
          </v-btn>
          <v-btn
              color="primary"
              variant="flat"
              :disabled="!tempNewName || tempNewName.trim() === ''"
              @click="saveRename"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
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
