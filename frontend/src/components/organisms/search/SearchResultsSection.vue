<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import {
  VCard,
  VCardText,
  VIcon,
  VContainer,
  VBtn,
  VTextField,
  VChip,
  VTooltip
} from 'vuetify/components';
import { FileText, Edit3, Paperclip, X } from 'lucide-vue-next';
import PaperList from '@/components/molecules/PaperList.vue';
import type { Paper } from '@/types/content';
import { useFileSelection } from '@/composables/useFileSelection';

const props = defineProps<{
  query: string;
  file: File | null;
  outputs: Paper[];
  showAbstract?: boolean;
  showAdd?: boolean;
}>();

const emit = defineEmits<{
  (e: 'add', paper: Paper): void;
  (e: 'updateQuery', payload: { query: string; file: File | null }): void;
  (e: 'view', paper: Paper): void;
}>();

// ----- Query & File State -----
const editableQuery = ref(props.query);

const {
  fileInput,
  selectedFile,
  triggerFileSelect,
  handleFileChange,
  removeFile
} = useFileSelection(props.file);

// Watch for external prop changes to keep local state in sync
watch(() => props.query, (newVal) => {
  editableQuery.value = newVal;
});
watch(() => props.file, (newVal) => {
  selectedFile.value = newVal;
});

// ----- Submission -----
const isChanged = computed(() => {
  const queryChanged = editableQuery.value.trim() !== props.query.trim();
  const fileChanged = selectedFile.value !== props.file;
  return queryChanged || fileChanged;
});

const handleQueryUpdate = () => {
  // Allow updating search if there is a text OR a file
  if (editableQuery.value.trim() || selectedFile.value) {
    emit('updateQuery', { query: editableQuery.value.trim(), file: selectedFile.value });
  }
};
</script>

<template>
  <v-container class="results-section">
    <v-card flat class="mb-8 pa-4 bg-blue-lighten-5 border-sm">
      <v-card-text class="d-flex align-start pa-0">
        <v-icon :icon="FileText" color="blue-darken-2" class="mt-1 me-3"></v-icon>
        <div class="flex-grow-1">
          <input
            ref="fileInput"
            type="file"
            accept="application/pdf"
            style="display: none"
            @change="handleFileChange"
          />

          <div class="d-flex align-center">
            <v-text-field
              v-model="editableQuery"
              label="Your Query"
              variant="outlined"
              density="compact"
              hide-details
              class="query-input flex-grow mb-2"
              @keyup.enter="handleQueryUpdate"
            >
              <template #append-inner>
                <v-chip
                  v-if="selectedFile"
                  closable
                  :close-icon="X"
                  color="primary"
                  variant="tonal"
                  size="small"
                  class="me-2"
                  @click:close="removeFile"
                >
                  {{ selectedFile.name }}
                </v-chip>

                <v-btn
                  icon
                  variant="text"
                  density="compact"
                  color="medium-emphasis"
                  @click="triggerFileSelect"
                >
                  <v-icon :icon="Paperclip" size="20" />
                  <v-tooltip activator="parent" loaction="top">Attach PDF</v-tooltip>
                </v-btn>
              </template>
            </v-text-field>

            <v-btn
              v-if="isChanged"
              color="primary"
              variant="outlined"
              size="small"
              class="ml-4"
              @click="handleQueryUpdate">
              <v-icon :icon="Edit3" start size="18"/>
              Update query
            </v-btn>
          </div>
        </div>
      </v-card-text>
    </v-card>

    <PaperList
      :papers="outputs"
      :show-abstract="showAbstract"
      :show-add="showAdd"
      title="Papers"
      empty-message="No results yet"
      :expand-all-on-change="true"
      @add="paper => emit('add', paper)"
      @view="paper => emit('view', paper)"
    />
  </v-container>
</template>

<style scoped>
.bg-blue-lighten-5 {
  background-color: var(--blue-lighten-5) !important;
}
.border-sm {
  border: 1px solid var(--border-sm-color-result);
}
</style>