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
  (e: 'submit', name: string, openImmediately: boolean): void;
}>();

const projectName = ref('');
const openAfterCreate = ref(false);

const close = () => {
  projectName.value = '';
  openAfterCreate.value = false;
  emit('update:modelValue', false);
};

const handleSubmit = () => {
  if (!projectName.value) return;
  emit('submit', projectName.value.trim(), openAfterCreate.value);
  projectName.value = '';
  openAfterCreate.value = false;
  close();
};

const toggleCheckbox = () => {
  openAfterCreate.value = !openAfterCreate.value;
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
              class="mb-2"
              autofocus
          />

          <div
              class="d-flex align-center mb-4 cursor-pointer"
              @click="toggleCheckbox"
          >
            <v-btn
                variant="outlined"
                class="pa-0 mr-3 rounded"
                :color="openAfterCreate ? 'black' : 'medium-emphasis'"
                height="20"
                width="20"
                min-width="20"
                flat
                :ripple="false"
            >
              <span v-if="openAfterCreate" class="text-caption font-weight-bold">✕</span>
            </v-btn>

            <span class="text-medium-emphasis user-select-none">
              Open project after create
            </span>
          </div>

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

<style scoped>
.user-select-none {
  user-select: none;
}
</style>