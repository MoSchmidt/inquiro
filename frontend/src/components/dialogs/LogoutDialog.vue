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
  <v-dialog :model-value="modelValue" @update:model-value="close" max-width="500">
    <v-card>
      <v-card-title class="text-h6 pa-4 pb-0">Log out</v-card-title>
      <v-card-text class="pa-4 text-medium-emphasis">
        Are you sure you want to log out?
      </v-card-text>
      <v-card-actions class="pa-4 pt-0">
        <v-spacer />
        <v-btn variant="text" class="text-medium-emphasis text-none" @click="close">Cancel</v-btn>
        <v-btn variant="text" color="error" class="text-none" @click="handleLogout">
          Log out
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>