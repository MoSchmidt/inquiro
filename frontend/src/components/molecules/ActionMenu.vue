<script setup lang="ts">
import { ref } from 'vue';
import {
  VBtn, VIcon, VList, VListItem, VMenu, VListItemTitle
} from 'vuetify/components';
import { MoreHorizontal } from 'lucide-vue-next';

export interface ActionMenuItem {
  title: string;
  value: string | number;
  icon?: any;
  color?: string;
  action?: () => void;
}

defineProps<{
  items: ActionMenuItem[];
  icon?: any;
}>();

const emit = defineEmits<{
  (e: 'select', item: ActionMenuItem): void;
}>();

const menuOpen = ref(false);

const handleItemClick = (item: ActionMenuItem) => {
  menuOpen.value = false;

  if (item.action) {
    item.action();
  }
  emit('select', item);
};
</script>

<template>
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
      <v-list-item
          v-for="(item, index) in items"
          :key="item.value || index"
          :value="item.value"
          :base-color="item.color"
          @click.stop="handleItemClick(item)"
      >
        <template v-if="item.icon" #prepend>
          <v-icon :icon="item.icon" size="18" class="me-2" />
        </template>

        <v-list-item-title>{{ item.title }}</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<style scoped>
.action-menu-btn {
  /* Optional styling */
}
</style>