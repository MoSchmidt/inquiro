<script setup lang="ts">
import {
  VDialog, VCard, VCardTitle, VCardText, VCardActions,
  VBtn, VSpacer
} from 'vuetify/components';

defineProps<{
  modelValue: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'logout'): void;
}>();

const close = () => {
  emit('update:modelValue', false);
};

const handleLogout = () => {
  emit('logout');
  close();
};
</script>

<template>
  <v-dialog
      :model-value="modelValue"
      @update:model-value="emit('update:modelValue', $event)"
      max-width="400"
  >
    <v-card>
      <v-card-title class="text-h5">Log out</v-card-title>
      <v-card-text>
        <p class="text-medium-emphasis">
          Are you sure you want to log out of your account?
        </p>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="secondary" variant="text" @click="close">
          Cancel
        </v-btn>
        <v-btn color="error" variant="text" @click="handleLogout">
          Log out
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>