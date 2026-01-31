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
    confirmationInput.value = '';
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
    <v-card>
      <v-card-title class="text-h6 pa-4 pb-0">Delete Project</v-card-title>
      <v-card-text class="pa-4">
        <p class="text-body-2 text-medium-emphasis mb-4">
          Are you sure you want to delete this project? This action cannot be undone. <br />
          Type <strong class="text-medium-emphasis">{{ projectName }}</strong> to confirm.
        </p>
        <v-form @submit.prevent="submitDelete">
          <v-text-field
              v-model="confirmationInput"
              label="Project Name"
              placeholder="Type project name here"
              variant="outlined"
              hide-details
        />
        </v-form>
      </v-card-text>

      <v-card-actions class="pa-4 pt-0">
        <v-spacer />
        <v-btn variant="text" class="text-medium-emphasis text-none" @click="close">Cancel</v-btn>
        <v-btn
            color="error"
            variant="text"
            class="text-none"
            :disabled="confirmationInput !== projectName"
            @click="submitDelete"
        >
          Delete
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
