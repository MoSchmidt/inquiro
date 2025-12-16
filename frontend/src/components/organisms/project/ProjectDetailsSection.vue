<script setup lang="ts">
import { ref } from 'vue';
import PaperList from '@/components/molecules/PaperList.vue';
import {
  VContainer,
  VTooltip
} from 'vuetify/components';
import { Pencil, Trash2 } from 'lucide-vue-next';
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
  (e: 'view', paper: Paper): void;
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
      :menu-options="menuOptions"
      title="Papers"
      empty-message="This project does not yet have any saved papers."
      :expand-all-on-change="false"
      @menu-select="handleMenuSelect"
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
