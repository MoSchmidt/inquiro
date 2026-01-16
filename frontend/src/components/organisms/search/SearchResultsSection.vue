<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import {
  VBtn,
  VCard,
  VCardText,
  VChip,
  VContainer,
  VIcon,
  VTextField,
  VTooltip,
} from 'vuetify/components';
import { Edit3, Paperclip, Sparkles, X } from 'lucide-vue-next';
import PaperList from '@/components/molecules/PaperList.vue';
import AdvancedSearchPanel from '@/components/organisms/search/AdvancedSearchPanel.vue';
import type { Paper, PaperMenuOption } from '@/types/content';
import type { AdvancedSearchOptions } from '@/types/search';
import { useFileSelection } from '@/composables/useFileSelection';

const props = defineProps<{
  query: string;
  file: File | null;
  outputs: Paper[];
  showAbstract?: boolean;
  showAdd?: boolean;
  advanced?: AdvancedSearchOptions;
}>();

const emit = defineEmits<{
  (e: 'add', paper: Paper): void;
  (
    e: 'updateQuery',
    payload: {
      query: string;
      file: File | null;
      advanced?: AdvancedSearchOptions;
    }
  ): void;
  (e: 'view', paper: Paper): void;
}>();

const menuOptions: PaperMenuOption[] = [
  { label: 'Summarise Paper', value: 'summarise', icon: Sparkles },
];

// ----- Query & File State -----
const editableQuery = ref(props.query);

const {
  fileInput,
  selectedFile,
  triggerFileSelect,
  handleFileChange,
  removeFile,
} = useFileSelection(props.file);

// ----- Advanced Options State -----
const getDefaultAdvancedOptions = (): AdvancedSearchOptions => ({
  yearFrom: undefined,
  yearTo: undefined,
  root: { type: 'group', operator: 'AND', children: [] },
});

const advancedOptions = ref<AdvancedSearchOptions>(
  props.advanced ?? getDefaultAdvancedOptions()
);

const isAdvancedValid = ref(true);

// Watch for external prop changes to keep local state in sync
watch(
  () => props.query,
  (newVal) => {
    editableQuery.value = newVal;
  }
);
watch(
  () => props.file,
  (newVal) => {
    selectedFile.value = newVal;
  }
);
watch(
  () => props.advanced,
  (newVal) => {
    advancedOptions.value = newVal ?? getDefaultAdvancedOptions();
  }
);

// ----- Submission -----
const isChanged = computed(() => {
  const queryChanged = editableQuery.value.trim() !== props.query.trim();
  const fileChanged = selectedFile.value !== props.file;
  const advancedChanged =
    JSON.stringify(advancedOptions.value) !==
    JSON.stringify(props.advanced ?? getDefaultAdvancedOptions());
  return queryChanged || fileChanged || advancedChanged;
});

const handleQueryUpdate = () => {
  // Allow updating search if there is a text OR a file
  if (editableQuery.value.trim() || selectedFile.value) {
    emit('updateQuery', {
      query: editableQuery.value.trim(),
      file: selectedFile.value,
      advanced: advancedOptions.value,
    });
  }
};
</script>

<template>
  <v-container class="results-section">
    <v-card flat class="mb-8 pa-4 border-sm" color="surface">
      <v-card-text class="d-flex align-start pa-0">
        <div class="flex-grow-1">
          <input
            id="pdf-upload"
            ref="fileInput"
            type="file"
            accept="application/pdf"
            style="display: none"
            aria-hidden="true"
            @change="handleFileChange"
          />

          <div class="d-flex align-center">
            <v-text-field
              v-model="editableQuery"
              label="Your Query"
              variant="outlined"
              density="compact"
              hide-details
              bg-color="surface"
              class="query-input flex-grow mb-2"
              aria-controls="pdf-upload"
              aria-label="Attach a PDF"
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
                  <v-tooltip activator="parent" location="top"
                    >Attach PDF</v-tooltip
                  >
                </v-btn>
              </template>
            </v-text-field>
          </div>
        </div>
      </v-card-text>

      <AdvancedSearchPanel
        class="mb-4"
        :initial-year-from="advancedOptions.yearFrom"
        :initial-year-to="advancedOptions.yearTo"
        :initial-root="advancedOptions.root"
        @update="(val, valid) => { advancedOptions = val; isAdvancedValid = valid; }"
      />

      <v-btn
        :disabled="!isChanged || !isAdvancedValid"
        color="primary"
        variant="outlined"
        size="small"
        class="ml-4"
        @click="handleQueryUpdate"
      >
        <v-icon :icon="Edit3" start size="18" />
        Update query
      </v-btn>
    </v-card>

    <PaperList
      :papers="outputs"
      :show-abstract="showAbstract"
      :show-add="showAdd"
      title="Papers"
      empty-message="No results yet"
      :expand-all-on-change="true"
      :menu-options="menuOptions"
      :search-context="query"
      @add="(paper) => emit('add', paper)"
      @view="(paper) => emit('view', paper)"
    />
  </v-container>
</template>

<style scoped></style>
