<script setup lang="ts">
import { ref, watch } from 'vue';
import { VDialog, VCard, VTextField, VCardActions, VSpacer, VBtn } from 'vuetify/components';

const props = defineProps<{
  modelValue: boolean;
  projectName: string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'submit'): void;
}>();

const confirmationInput = ref('');

watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    confirmationInput.value = ''; // Reset bei jedem Öffnen
  }
});

const close = () => {
  emit('update:modelValue', false);
};

const submitDelete = () => {
  if (confirmationInput.value === props.projectName) {
    emit('submit');
    close();
  }
};
</script>

<template>
  <v-dialog :model-value="modelValue" @update:model-value="close" max-width="500">
    <v-card class="pa-4">
      <h3 class="text-h6 mb-4">Delete Project</h3>

      <p class="text-body-2 text-medium-emphasis mb-4">
        Are you sure you want to delete this project? This action cannot be undone. <br />
        Type <strong class="text-high-emphasis">{{ projectName }}</strong> to confirm.
      </p>

      <v-text-field
          v-model="confirmationInput"
          label="Project Name"
          placeholder="Type project name here"
          variant="outlined"
          color="error"
          autofocus
          @keyup.enter="submitDelete"
      ></v-text-field>

      <v-card-actions class="px-0">
        <v-spacer></v-spacer>
        <v-btn variant="text" color="grey-darken-1" @click="close">
          Cancel
        </v-btn>
        <v-btn
            color="error"
            variant="flat"
            :disabled="confirmationInput !== projectName"
            @click="submitDelete"
        >
          Delete
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>