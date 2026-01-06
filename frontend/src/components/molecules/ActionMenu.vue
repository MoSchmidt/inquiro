<script setup lang="ts">
import { ref } from 'vue';
import type { Component } from 'vue';
import {
  VBtn, VIcon, VList, VListItem, VMenu, VListItemTitle
} from 'vuetify/components';
import { MoreHorizontal } from 'lucide-vue-next';
import type { ActionMenuItem } from '@/types/ui';

defineProps<{
  items: ActionMenuItem[];
  icon?: Component;
}>();

const emit = defineEmits<{
  (e: 'select', item: ActionMenuItem): void;
}>();

const menuOpen = ref(false);

const handleItemClick = (item: ActionMenuItem) => {
  if (item.disabled) return;

  menuOpen.value = false;

  if (item.action) {
    item.action();
  }
  emit('select', item);
};
</script>

<template>
  <div @click.stop>
    <v-menu v-model="menuOpen" location="bottom end">
      <template #activator="{ props: menuProps }">
        <v-btn
            icon
            size="small"
            variant="text"
            v-bind="menuProps"
            class="action-menu-btn"
            @click.stop
        >
          <v-icon :icon="icon || MoreHorizontal" size="18" />
        </v-btn>
      </template>

      <v-list density="compact">
        <template v-for="(item, index) in items" :key="item.value || index">
          <v-list-item
              v-if="!item.hidden"
              :value="item.value"
              :base-color="item.color"
              :disabled="item.disabled"
              @click.stop="handleItemClick(item)"
          >
            <template v-if="item.icon" #prepend>
              <v-icon :icon="item.icon" size="18" class="me-2" />
            </template>

            <v-list-item-title>{{ item.title }}</v-list-item-title>
          </v-list-item>
        </template>
      </v-list>
    </v-menu>
  </div>
</template>