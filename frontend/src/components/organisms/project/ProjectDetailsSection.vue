<script setup lang="ts">
import { ref } from 'vue';
import PaperList from '@/components/molecules/PaperList.vue';
import {
  VCard,
  VCardText,
  VIcon,
  VBtn,
  VContainer,
  VTooltip
} from 'vuetify/components';
import { FileText, Trash2, Pencil } from 'lucide-vue-next';
import type { Paper, PaperMenuOption } from '@/types/content';

import RenameProjectDialog from '@/components/dialogs/RenameProjectDialog.vue';

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

const handleRenameSubmit = (newName: string) => {
  emit('rename', newName);
  isRenameDialogOpen.value = false;
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
              @click="isRenameDialogOpen = true"
          >
            <v-icon :icon="Pencil" size="20" />
            <v-tooltip activator="parent" location="top">
              Rename project
            </v-tooltip>
          </v-btn>
        </div>
        <p class="text-caption text-medium-emphasis">
          {{ papers.length }} saved papers
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

    <RenameProjectDialog
        v-model="isRenameDialogOpen"
        :current-name="projectName"
        @submit="handleRenameSubmit"
    />

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