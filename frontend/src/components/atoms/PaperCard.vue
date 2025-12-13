<script setup lang="ts">
import {
  VBtn,
  VExpansionPanelText,
  VExpansionPanelTitle,
  VIcon,
} from 'vuetify/components';
import { ChevronDown, FolderPlus } from 'lucide-vue-next';
import { withDefaults, computed } from 'vue';
import type { Paper, PaperMenuOption } from '@/types/content';
import ActionMenu, { type ActionMenuItem } from '@/components/molecules/ActionMenu.vue';

const props = withDefaults(
    defineProps<{
      paper: Paper;
      showAbstract?: boolean;
      showAdd?: boolean;
      menuOptions?: PaperMenuOption[];
    }>(),
    {
      showAbstract: true,
      showAdd: false,
      menuOptions: () => [] as PaperMenuOption[],
    }
);

const emit = defineEmits<{
  (e: 'add', paper: Paper): void;
  (e: 'menu-select', payload: { option: PaperMenuOption; paper: Paper }): void;
}>();

// Transform PaperMenuOption to ActionMenuItem
const transformedMenuOptions = computed<ActionMenuItem[]>(() => {
  return props.menuOptions.map(option => ({
    title: option.label,
    value: option.value,
    icon: option.icon,
    // When clicked, we emit the original event format expected by the parent
    action: () => emit('menu-select', { option, paper: props.paper })
  }));
});
</script>

<template>
  <v-expansion-panel-title v-slot="{ expanded }">
    <div class="paper-header w-100">
      <div class="expand-icon-wrapper flex items-center justify-center">
        <v-icon
          :icon="ChevronDown"
          size="18"
          class="expand-icon"
          :class="{ 'expand-icon--expanded': expanded }"
        />
      </div>

      <div class="flex-grow-1 me-sm-4">
        <div class="d-flex align-center">
          <div
            class="text-subtitle-1 font-weight-medium paper-title text-truncate"
          >
            {{ paper.title }}
          </div>
          <span
            v-if="paper.year"
            class="ms-2"
            style="color: grey; font-size: 0.85rem"
            >
            {{ paper.year }}
          </span>
        </div>
        <div class="text-body-2 text-medium-emphasis paper-meta">
          <span v-if="paper.author">{{ paper.author }}</span>
        </div>
      </div>

      <div class="action-buttons">
        <v-btn
          v-if="showAdd"
          icon
          size="small"
          variant="text"
          color="primary"
          @click.stop="emit('add', paper)"
        >
          <v-icon :icon="FolderPlus" size="16" />
        </v-btn>

        <ActionMenu
            v-if="transformedMenuOptions.length"
            :items="transformedMenuOptions"
        />
      </div>
    </div>
  </v-expansion-panel-title>

  <v-expansion-panel-text>
    <div class="text-body-2 text-medium-emphasis mb-3 paper-abstract">
      <span v-if="showAbstract && paper.abstract"> {{ paper.abstract }} </span>
      <span v-else class="text-disabled"> No abstract available. </span>
    </div>
  </v-expansion-panel-text>
</template>

<style scoped>
.paper-header {
  padding-right: 4px;
  cursor: pointer;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  column-gap: 12px;
  align-items: center;
}

.paper-meta { font-size: 0.85rem; }

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
  flex-shrink: 0;
}

.expand-icon { transition: transform 0.2s ease; }
.expand-icon--expanded { transform: rotate(180deg); }

.action-buttons :deep(.v-btn) { margin-left: 0; }
</style>