<script setup lang="ts">
import { ref, watch, nextTick, computed, withDefaults } from 'vue';
import { VExpansionPanel, VExpansionPanels } from 'vuetify/components';
import type { Paper, PaperMenuOption } from './types';
import PaperCard from './PaperCard.vue';

interface Props {
  papers: Paper[];
  showAbstract?: boolean;
  showAdd?: boolean;
  title?: string;
  emptyMessage?: string;
  expandAllOnChange?: boolean;
  menuOptions?: PaperMenuOption[];
}

const props = withDefaults(defineProps<Props>(), {
  showAbstract: true,
  showAdd: false,
  title: 'Artikel',
  emptyMessage: 'Keine Ergebnisse vorhanden.',
  expandAllOnChange: false,
  menuOptions: () => [] as PaperMenuOption[],
});

const emit = defineEmits<{
  add: [paper: Paper];
  'menu-select': [{ option: PaperMenuOption; paper: Paper }];
}>();

const expanded = ref<(number | string)[]>([]);

watch(
  () => props.papers,
  (newPapers) => {
    if (props.expandAllOnChange && newPapers.length > 0) {
      nextTick(() => {
        expanded.value = newPapers.map((p) => p.paper_id);
      });
    } else if (!props.expandAllOnChange) {

      expanded.value = expanded.value.filter((id) =>
        newPapers.some((p) => p.paper_id === id)
      );
    }
  },
  { immediate: props.expandAllOnChange }
);

// Event handlers
const handleAdd = (paper: Paper) => emit('add', paper);
const handleMenuSelect = (payload: { option: PaperMenuOption; paper: Paper }) =>
  emit('menu-select', payload);
</script>

<template>
  <section class="paper-list">
    <h3 class="text-h6 mb-4">
      {{ title }}
      <span class="text-medium-emphasis">({{ papers.length }})</span>
    </h3>

    <v-expansion-panels
      v-if="papers.length"
      v-model="expanded"
      multiple
      class="paper-panels"
      :rounded="false"
    >
      <v-expansion-panel
        v-for="paper in papers"
        :key="paper.paper_id"
        :value="paper.paper_id"
        elevation="1"
        class="paper-panel mb-3"
        rounded="xl"
        :ripple="false"
        style="border-radius: 12px !important"
      >
        <PaperCard
          :paper="paper"
          :show-abstract="showAbstract"
          :show-add="showAdd"
          :menu-options="menuOptions"
          @add="handleAdd"
          @menu-select="handleMenuSelect"
        />
      </v-expansion-panel>
    </v-expansion-panels>

    <div v-else class="empty-state text-center py-12">
      <p class="text-medium-emphasis">
        {{ emptyMessage }}
      </p>
    </div>
  </section>
</template>

<style scoped>
.paper-list {
  container-type: inline-size;
}

.paper-panels {
  will-change: auto;
}

.paper-panel {
  border: 1px solid rgba(0, 0, 0, 0.05) !important;
  border-top: none !important;
  transition: box-shadow 0.2s ease;
  border-radius: 12px !important;
  overflow: hidden !important;
}

.paper-panel:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
}

.empty-state {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.v-expansion-panel:not(:first-child)::after),
:deep(.v-expansion-panel:not(:first-child) .v-expansion-panel-title::after) {
  display: none !important;
  border: none !important;
  box-shadow: none !important;
  height: 0 !important;
  opacity: 0 !important;
}
</style>
