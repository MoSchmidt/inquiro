<script setup lang="ts">
import { ref } from 'vue';
import { VCard, VCardTitle, VCardText, VTextarea, VBtn, VIcon, VRow, VCol, VChip, VContainer } from 'vuetify/components';
import { Send, Paperclip, X } from 'lucide-vue-next';
import { useFileSelection } from '@/composables/useFileSelection';

const emit = defineEmits<{
  (e: 'submit', payload: { query: string; file: File | null }): void
}>();

const input = ref('');

const {
  fileInput,
  selectedFile,
  triggerFileSelect,
  handleFileChange,
  removeFile
} = useFileSelection();

const handleSubmit = () => {
  if (input.value.trim() || selectedFile.value) {
    emit('submit', { query: input.value, file: selectedFile.value });
    input.value = '';
    removeFile();
  }
};
</script>

<template>
  <div class="input-wrapper">
    <v-container fluid class="fill-height align-center justify-center">
      <div class="w-100" style="max-width: 900px;">
        <div class="text-center mb-10">
          <h2 class="text-h4 mb-2">Welcome to Inquiro</h2>
          <p class="text-medium-emphasis">
            Enter your text input below and let our AI generate powerful results for you
          </p>
        </div>

        <v-form @submit.prevent="handleSubmit">
          <input
            ref="fileInput"
            type="file"
            accept="application/pdf"
            style="display: none"
            @change="handleFileChange"
          />

          <div class="textarea-container mb-4">
            <v-textarea
              v-model="input"
              label="Enter your text here..."
              variant="outlined"
              auto-grow
              rows="8"
              class="mb-4"
              bg-color="white"
              hide-details
            ></v-textarea>

            <div class="add-pdf-actions">
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
                <v-icon :icon="Paperclip" size="22" />
                <v-tooltip activator="parent" location="top">Attach PDF</v-tooltip>
              </v-btn>
            </div>
          </div>

          <v-btn
              type="submit"
              color="primary"
              block
              size="large"
              :disabled="!input.trim() && !selectedFile"
          >
            <v-icon :icon="Send" start></v-icon>
            Generate results
          </v-btn>
        </v-form>

        <v-row class="mt-12">
          <v-col cols="12" md="4">
            <v-card flat class="pa-4 text-center border-sm">
              <div class="d-flex align-center justify-center mx-auto mb-4 bg-blue-lighten-4 rounded-circle" style="width: 48px; height: 48px;">
                <span class="text-blue-darken-2 text-h6">1</span>
              </div>
              <v-card-title class="text-h6 mb-2 pa-0">Input</v-card-title>
              <v-card-text class="text-medium-emphasis pa-0 text-body-2">
                Enter your text query or request
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card flat class="pa-4 text-center border-sm">
              <div class="d-flex align-center justify-center mx-auto mb-4 bg-blue-lighten-4 rounded-circle" style="width: 48px; height: 48px;">
                <span class="text-blue-darken-2 text-h6">2</span>
              </div>
              <v-card-title class="text-h6 mb-2 pa-0">AI Processing</v-card-title>
              <v-card-text class="text-medium-emphasis pa-0 text-body-2">
                Our AI evaluates and processes your input
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card flat class="pa-4 text-center border-sm">
              <div class="d-flex align-center justify-center mx-auto mb-4 bg-blue-lighten-4 rounded-circle" style="width: 48px; height: 48px;">
                <span class="text-blue-darken-2 text-h6">3</span>
              </div>
              <v-card-title class="text-h6 mb-2 pa-0">Results</v-card-title>
              <v-card-text class="text-medium-emphasis pa-0 text-body-2">
                Receive organized results
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </div>
    </v-container>
  </div>

</template>

<style scoped>
/* Prefer Vuetify classes, but include a few custom styles for the circles */
.bg-blue-lighten-4 {
  background-color: var(--blue-lighten-4) !important;
}
.text-blue-darken-2 {
  color: var(--blue-darken-2) !important;
}
.border-sm {
  border: 1px solid var(--border-sm-color);
}
.textarea-container  {
  position: relative;
}
.textarea-container :deep(.v-field__input) {
  padding-bottom: 40px; /* Adjust this value if needed */
}
.add-pdf-actions {
  position: absolute;
  bottom: 8px;
  right: 12px;
  display: flex;
  align-items: center;
  z-index: 1;
}
</style>