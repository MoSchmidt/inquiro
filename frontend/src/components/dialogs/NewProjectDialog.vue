<script setup lang="ts">
import { ref } from 'vue';
import {
  VDialog, VCard, VCardTitle, VCardText, VCardActions,
  VForm, VTextField, VBtn, VSpacer
} from 'vuetify/components';

const props = defineProps<{
  modelValue: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'submit', name: string): void;
}>();

const projectName = ref('');

const close = () => {
  projectName.value = '';
  emit('update:modelValue', false);
};

const handleSubmit = () => {
  if (!projectName.value) return;
  emit('submit', projectName.value.trim());
  projectName.value = '';
  close();
};
</script>

<template>
  <v-dialog
      :model-value="modelValue"
      @update:model-value="emit('update:modelValue', $event)"
      max-width="500"
  >
    <v-card>
      <v-card-title class="text-h5">New Project</v-card-title>
      <v-card-text>
        <p class="mb-4 text-medium-emphasis">
          Enter a name for your new project.
        </p>
        <v-form @submit.prevent="handleSubmit">
          <v-text-field
              v-model="projectName"
              label="Project name"
              variant="outlined"
              required
              class="mb-4"
              autofocus
          />
          <v-btn type="submit" color="primary" block>Create Project</v-btn>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="secondary" variant="text" @click="close">
          Close
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>