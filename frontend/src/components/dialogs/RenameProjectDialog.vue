<script setup lang="ts">
import { ref, watch } from 'vue';
import { VDialog, VCard, VTextField, VCardActions, VSpacer, VBtn } from 'vuetify/components';

const props = defineProps<{
  modelValue: boolean;
  currentName: string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'submit', newName: string): void;
}>();

const tempName = ref('');

watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    tempName.value = props.currentName;
  }
});

const close = () => {
  emit('update:modelValue', false);
};

const save = () => {
  const trimmed = tempName.value.trim();
  if (trimmed) {
    emit('submit', trimmed);
    close();
  }
};
</script>

<template>
  <v-dialog :model-value="modelValue" @update:model-value="close" max-width="500">
    <v-card>
      <v-card-title class="text-h6 pa-4 pb-0">Rename Project</v-card-title>
      <v-card-text class="pa-4">
        <v-form @submit.prevent="save">
          <v-text-field
              v-model="tempName"
              label="Project Name"
              variant="outlined"
              hide-details
              autofocus
          />
        </v-form>
      </v-card-text>
      <v-card-actions class="pa-4 pt-0">
        <v-spacer />
        <v-btn variant="text" class="text-medium-emphasis text-none" @click="close">Cancel</v-btn>
        <v-btn variant="text" color="secondary" class="text-none" :disabled="!tempName || tempName.trim() === ''" @click="save">
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>