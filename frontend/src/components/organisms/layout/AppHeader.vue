<script setup lang="ts">
import { VAppBar, VBtn, VIcon, VToolbarTitle, VSpacer, VTooltip } from 'vuetify/components';
import { Menu as MenuIcon, Sun, Moon } from 'lucide-vue-next';
import { useTheme } from '@/composables/useTheme';

defineProps<{
  isAuthenticated: boolean;
  showNewQuery?: boolean;
}>();

const { isDark, toggleTheme } = useTheme();
const emit = defineEmits<{
  (e: 'toggleSidebar'): void;
  (e: 'newQuery'): void;
  (e: 'openCreateAccount'): void;
}>();
</script>

<template>
  <v-app-bar app flat border>
    <v-btn icon variant="text" @click="emit('toggleSidebar')">
      <v-icon :icon="MenuIcon" />
    </v-btn>
    <v-toolbar-title class="text-h6">Inquiro</v-toolbar-title>
    <v-spacer></v-spacer>

    <v-btn icon variant="text" @click="toggleTheme()">
      <v-icon :icon="isDark ? Sun : Moon" />
      <v-tooltip activator="parent" location="bottom">
        {{ isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode' }}
      </v-tooltip>
    </v-btn>

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
