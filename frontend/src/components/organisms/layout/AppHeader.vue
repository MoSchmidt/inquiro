<script setup lang="ts">
import { VAppBar, VBtn, VIcon, VToolbarTitle, VSpacer } from 'vuetify/components';
import { Menu as MenuIcon } from 'lucide-vue-next';

defineProps<{
  isAuthenticated: boolean;
  showNewQuery?: boolean;
}>();

const emit = defineEmits<{
  (e: 'toggleSidebar'): void;
  (e: 'newQuery'): void;
  (e: 'openCreateAccount'): void;
}>();
</script>

<template>
  <v-app-bar app color="white" flat border>
    <v-btn icon variant="text" @click="emit('toggleSidebar')">
      <v-icon :icon="MenuIcon" />
    </v-btn>
    <v-toolbar-title class="text-h6">Inquiro</v-toolbar-title>
    <v-spacer></v-spacer>

    <v-btn
      v-if="!isAuthenticated"
      variant="text"
      color="primary"
      class="mr-2"
      @click="emit('openCreateAccount')"
    >
      Create Account
    </v-btn>

    <v-btn
      v-if="showNewQuery"
      @click="emit('newQuery')"
      variant="outlined"
      color="primary"
    >
      New Query
    </v-btn>
  </v-app-bar>
</template>

<style scoped></style>
