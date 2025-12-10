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
    <v-card class="pa-4">
      <h3 class="text-h6 mb-4">Rename Project</h3>

      <v-text-field
          v-model="tempName"
          label="Project Name"
          variant="outlined"
          autofocus
          @keyup.enter="save"
      ></v-text-field>

      <v-card-actions class="px-0">
        <v-spacer></v-spacer>
        <v-btn variant="text" color="grey-darken-1" @click="close">
          Cancel
        </v-btn>
        <v-btn
            color="primary"
            variant="flat"
            :disabled="!tempName || tempName.trim() === ''"
            @click="save"
        >
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>