<script setup lang="ts">
import { ref } from 'vue';
import PaperList from '@/components/molecules/PaperList.vue';
import {
  VContainer,
  VTooltip,
  VBtn,
  VIcon
} from 'vuetify/components';
import { Pencil, Sparkles, Trash2 } from 'lucide-vue-next';
import type { Paper } from '@/types/content';
import type { ActionMenuItem } from '@/types/ui';
import { usePaperSummariesStore } from '@/stores/paperSummaries';

import RenameProjectDialog from '@/components/dialogs/RenameProjectDialog.vue';
defineProps<{
  projectName: string;
  papers: Paper[];
  showAbstract?: boolean;
}>();

const emit = defineEmits<{
  (e: 'remove', paper: Paper): void;
  (e: 'rename', newName: string): void;
  (e: 'view', paper: Paper): void;
}>();

const isRenameDialogOpen = ref(false);
const summariesStore = usePaperSummariesStore();

const handleRenameSubmit = (newName: string) => {
  emit('rename', newName);
  isRenameDialogOpen.value = false;
};

// --- Action Provider ---
// This function is passed down to PaperList -> PaperCard
const getPaperActions = (paper: Paper): ActionMenuItem[] => [
  {
    title: 'Summarise Paper',
    value: 'summarise',
    icon: Sparkles,
    action: () => summariesStore.summarise(paper.paper_id, { query: '' })
  },
  {
    title: 'Remove from Project',
    value: 'remove',
    icon: Trash2,
    color: 'error',
    action: () => emit('remove', paper)
  },
];
</script>

<template>
  <v-container class="py-6" style="max-width: 1200px">
    <div class="d-flex align-center mb-2">
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

    <PaperList
        :papers="papers"
        :show-abstract="showAbstract"
        :show-add="false"
        :action-provider="getPaperActions"
        title="Papers"
        empty-message="This project does not yet have any saved papers."
        :expand-all-on-change="false"
        @view="(p) => emit('view', p)"
    />

    <RenameProjectDialog
        v-model="isRenameDialogOpen"
        :current-name="projectName"
        @submit="handleRenameSubmit"
    />

  </v-container>
</template>

<style scoped>

.project-title {
  font-size: 1.8rem;
  font-weight: 650;
  letter-spacing: 0.02em;
}
</style>