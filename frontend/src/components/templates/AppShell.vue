<script setup lang="ts">
import { VApp, VAppBar, VLayout, VMain, VNavigationDrawer } from 'vuetify/components';

const props = defineProps<{ drawerOpen: boolean }>();
const emit = defineEmits<{ (e: 'update:drawerOpen', value: boolean): void }>();

const updateDrawer = (value: boolean) => emit('update:drawerOpen', value);
</script>

<template>
  <v-app>
    <v-layout>
      <v-navigation-drawer
        :model-value="props.drawerOpen"
        location="left"
        temporary
        width="320"
        @update:model-value="updateDrawer"
      >
        <slot name="drawer" />
      </v-navigation-drawer>

      <v-app-bar app color="white" flat border>
        <slot name="app-bar" />
      </v-app-bar>

      <v-main class="bg-grey-lighten-4">
        <slot />
      </v-main>
    </v-layout>
    <slot name="dialogs" />
  </v-app>
</template>
