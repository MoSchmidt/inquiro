<script setup lang="ts">
import { ref } from 'vue';
import { VCard, VCardTitle, VCardText, VTextarea, VBtn, VIcon, VRow, VCol, VChip, VContainer, VForm } from 'vuetify/components';
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
    emit('submit', { query: input.value.trim(), file: selectedFile.value });
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
              id="pdf-upload"
              ref="fileInput"
              type="file"
              accept="application/pdf"
              style="display: none"
              aria-hidden="true"
              @change="handleFileChange"
          />

          <div class="textarea-container mb-4">
            <v-textarea
                v-model="input"
                label="Enter your text here..."
                variant="outlined"
                auto-grow
                rows="8"
                bg-color="surface"
                hide-details
                class="search-textarea"
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
                  aria-controls="pdf-upload"
                  aria-label="Upload a PDF file"
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
              class="generate-btn"
          >
            <v-icon :icon="Send" start></v-icon>
            Generate results
          </v-btn>
        </v-form>

        <v-row class="mt-12">
          <v-col cols="12" md="4">
            <v-card
                flat
                border
                class="pa-4 text-center border-border-light"
            >
              <div class="d-flex align-center justify-center mx-auto mb-4 bg-step-surface rounded-circle" style="width: 48px; height: 48px;">
                <span class="text-step-text text-h6">1</span>
              </div>
              <v-card-title class="text-h6 mb-2 pa-0">Input</v-card-title>
              <v-card-text class="text-medium-emphasis pa-0 text-body-2">
                Enter your text query or request
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card
                flat
                border
                class="pa-4 text-center border-border-light"
            >
              <div class="d-flex align-center justify-center mx-auto mb-4 bg-step-surface rounded-circle" style="width: 48px; height: 48px;">
                <span class="text-step-text text-h6">2</span>
              </div>
              <v-card-title class="text-h6 mb-2 pa-0">AI Processing</v-card-title>
              <v-card-text class="text-medium-emphasis pa-0 text-body-2">
                Our AI evaluates and processes your input
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card
                flat
                border
                class="pa-4 text-center border-border-light"
            >
              <div class="d-flex align-center justify-center mx-auto mb-4 bg-step-surface rounded-circle" style="width: 48px; height: 48px;">
                <span class="text-step-text text-h6">3</span>
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
.textarea-container {
  position: relative;
}

.add-pdf-actions {
  position: absolute;
  bottom: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  z-index: 10;
}

:deep(.v-field__input) {
  padding-bottom: 40px !important;
}
</style>

<style>

.v-theme--dark .generate-btn.v-btn--disabled {
  background-color: rgba(112, 146, 189, 1) !important;
  color: rgba(255, 255, 255, 0.3) !important;
  opacity: 1 !important;
}

.v-theme--dark .generate-btn.v-btn--disabled .v-btn__overlay {
  opacity: 0 !important;
  display: none !important;
}
</style>