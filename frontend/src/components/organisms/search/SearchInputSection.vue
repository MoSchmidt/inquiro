<script setup lang="ts">
import { ref } from 'vue';
import {
  VBtn,
  VCard,
  VCardText,
  VCardTitle,
  VCol,
  VContainer,
  VForm,
  VIcon,
  VRow,
  VTextarea,
} from 'vuetify/components';
import { Send } from 'lucide-vue-next';
import type { AdvancedSearchOptions } from '@/types/search';
import AdvancedSearchPanel from '@/components/atoms/AdvancedSearchPanel.vue';

const emit = defineEmits<{
  (
    e: 'submit',
    payload: { query: string; advanced?: AdvancedSearchOptions }
  ): void;
}>();

const input = ref('');

const advancedOptions = ref<AdvancedSearchOptions>({
  yearFrom: undefined,
  yearTo: undefined,
  root: {
    type: 'group',
    operator: 'AND',
    children: [],
  },
});

const handleSubmit = () => {
  if (input.value.trim()) {
    emit('submit', {
      query: input.value,
      advanced: advancedOptions.value,
    });
    // keep query text or clear, up to you:
    // input.value = ''
  }
};
</script>

<template>
  <div class="input-wrapper">
    <v-container fluid class="fill-height align-center justify-center">
      <div class="w-100" style="max-width: 900px">
        <div class="text-center mb-10">
          <h2 class="text-h4 mb-2">Welcome to Inquiro</h2>
          <p class="text-medium-emphasis">
            Enter your text input below and let our AI generate powerful results
            for you
          </p>
        </div>

        <v-form @submit.prevent="handleSubmit">
          <v-textarea
            v-model="input"
            placeholder="Enter your text here..."
            variant="solo"
            rounded="lg"
            auto-grow
            flat
            rows="8"
            class="mb-4 shadow-xl custom-shadow-textarea"
            bg-color="white"
          />

          <AdvancedSearchPanel
            class="mb-4"
            @update="(val) => (advancedOptions = val)"
          />

          <v-btn
            type="submit"
            color="primary"
            block
            size="large"
            :disabled="!input.trim()"
          >
            <v-icon :icon="Send" start />
            Generate results
          </v-btn>
        </v-form>

        <!-- Your step cards unchanged -->
        <v-row class="mt-12">
          <v-col cols="12" md="4">
            <v-card flat class="pa-4 text-center border-sm">
              <div
                class="d-flex align-center justify-center mx-auto mb-4 bg-blue-lighten-4 rounded-circle"
                style="width: 48px; height: 48px"
              >
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
              <div
                class="d-flex align-center justify-center mx-auto mb-4 bg-blue-lighten-4 rounded-circle"
                style="width: 48px; height: 48px"
              >
                <span class="text-blue-darken-2 text-h6">2</span>
              </div>
              <v-card-title class="text-h6 mb-2 pa-0"
                >AI Processing</v-card-title
              >
              <v-card-text class="text-medium-emphasis pa-0 text-body-2">
                Our AI evaluates and processes your input
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card flat class="pa-4 text-center border-sm">
              <div
                class="d-flex align-center justify-center mx-auto mb-4 bg-blue-lighten-4 rounded-circle"
                style="width: 48px; height: 48px"
              >
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
.bg-blue-lighten-4 {
  background-color: var(--blue-lighten-4) !important;
}
.text-blue-darken-2 {
  color: var(--blue-darken-2) !important;
}
.border-sm {
  border: 1px solid var(--border-sm-color);
}

.custom-shadow-textarea :deep(.v-field) {
  box-shadow: var(--shadow-small);
  border-radius: var(--radius-default);
}
</style>