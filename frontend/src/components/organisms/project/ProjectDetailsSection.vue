<script setup lang="ts">
import { ref } from 'vue';
import PaperList from '@/components/molecules/PaperList.vue';
import {
  VBtn,
  VCard,
  VCardActions,
  VContainer,
  VDialog,
  VIcon,
  VSpacer,
  VTextField,
  VTooltip,
} from 'vuetify/components';
import { Pencil, Trash2 } from 'lucide-vue-next';
import type { Paper, PaperMenuOption } from '@/types/content';

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
        :ripple="false"
        @click="openRenameDialog"
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
