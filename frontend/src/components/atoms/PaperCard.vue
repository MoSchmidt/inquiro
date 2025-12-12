<script setup lang="ts">
import {
  VBtn,
  VExpansionPanelText,
  VExpansionPanelTitle,
  VIcon,
  VList,
  VListItem,
  VListItemTitle,
  VMenu,
} from 'vuetify/components';
import { ChevronDown, FolderPlus, MoreHorizontal, Eye } from 'lucide-vue-next';
import { withDefaults } from 'vue';
import type { Paper, PaperMenuOption } from '@/types/content';

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
  (e: 'view', paper: Paper): void;
}>();
</script>

<template>
  <v-expansion-panel-title v-slot="{ expanded }">
    <div class="paper-header w-100">
      <!-- Expand icon -->
      <div class="expand-icon-wrapper flex items-center justify-center">
        <v-icon
          :icon="ChevronDown"
          size="18"
          class="expand-icon"
          :class="{ 'expand-icon--expanded': expanded }"
        />
      </div>

      <!-- Title + meta -->
      <div class="flex-grow-1 me-sm-4">
        <div class="d-flex align-center">
          <div
            class="text-subtitle-1 font-weight-medium paper-title text-truncate"
          >
            {{ paper.title }}
          </div>

          <!-- Year next to title -->
          <span
            v-if="paper.year"
            class="ms-2"
            style="color: grey; font-size: 0.85rem"
            >
            {{ paper.year }}
          </span>
        </div>

        <!-- Author etc. meta stays below -->
        <div class="text-body-2 text-medium-emphasis paper-meta">
          <span v-if="paper.author">{{ paper.author }}</span>
        </div>
      </div>

      <!-- Right actions stay the same -->
      <div class="action-buttons">
        <v-btn
            icon
            size="small"
            variant="text"
            color="primary"
            class="me-1"
            @click.stop="emit('view', paper)"
        >
          <v-icon :icon="Eye" size="18" />
          <v-tooltip activator="parent" location="top">Read Paper</v-tooltip>
        </v-btn>
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

        <v-menu
          v-if="menuOptions && menuOptions.length"
          location="bottom end"
          offset="4"
        >
          <template #activator="{ props: activatorProps }">
            <v-btn
              icon
              size="small"
              variant="text"
              v-bind="activatorProps"
              @click.stop
            >
              <v-icon :icon="MoreHorizontal" size="18" />
            </v-btn>
          </template>

          <v-list density="compact">
            <v-list-item
              v-for="option in menuOptions"
              :key="option.value"
              @click.stop="emit('menu-select', { option, paper })"
            >
              <template v-if="option.icon" #prepend>
                <component
                  :is="option.icon"
                  size="16"
                  class="me-2 text-gray-500"
                />
              </template>
              <v-list-item-title>{{ option.label }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
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

.paper-meta {
  font-size: 0.85rem;
}

.expand-icon {
  transition: transform 0.18s ease;
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
  flex-shrink: 0;
}

.expand-icon {
  transition: transform 0.2s ease;
}
.expand-icon--expanded {
  transform: rotate(180deg);
}

.action-buttons :deep(.v-btn) {
  margin-left: 0;
}
</style>