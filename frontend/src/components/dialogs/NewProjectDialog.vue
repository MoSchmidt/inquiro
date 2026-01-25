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
const openAfterCreate = ref(true);

const close = () => {
  projectName.value = '';
  openAfterCreate.value = true;
  emit('update:modelValue', false);
};

const handleSubmit = () => {
  if (!projectName.value) return;
  emit('submit', projectName.value.trim(), openAfterCreate.value);
  projectName.value = '';
  openAfterCreate.value = true;
  close();
};

</script>

<template>
  <v-dialog :model-value="modelValue" @update:model-value="close" max-width="500">
    <v-card>
      <v-card-title class="text-h6 pa-4 pb-0">New Project</v-card-title>
      <v-card-text class="pa-4">
        <v-form @submit.prevent="handleSubmit">
          <v-text-field
              v-model="projectName"
              label="Project name"
              variant="outlined"
              required
              autofocus
              class="mb-2"
          />

          <div class="d-flex align-center cursor-pointer" @click="openAfterCreate = !openAfterCreate">
            <v-btn
                variant="outlined"
                class="pa-0 mr-3 rounded"
                :color="openAfterCreate ? 'secondary' : 'medium-emphasis'"
                height="20" width="20" min-width="20" flat :ripple="false"
            >
              <span v-if="openAfterCreate" class="text-caption font-weight-bold">✕</span>
            </v-btn>
            <span class="text-medium-emphasis user-select-none">Open project after create</span>
          </div>
        </v-form>
      </v-card-text>

      <v-card-actions class="pa-4 pt-0">
        <v-spacer />
        <v-btn variant="text" class="text-medium-emphasis text-none" @click="close">Cancel</v-btn>
        <v-btn
            color="secondary"
            variant="text"
            class="text-none"
            :disabled="!projectName"
            @click="handleSubmit"
        >
          Create Project
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
