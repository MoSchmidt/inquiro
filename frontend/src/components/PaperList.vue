<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue';
import { VExpansionPanel, VExpansionPanels } from 'vuetify/components';
import type { Paper } from './types';
import PaperCard from './PaperCard.vue';

interface Props {
  papers: Paper[];
  showAbstract?: boolean;
  showAdd?: boolean;
  showRemove?: boolean;
  title?: string;
  emptyMessage?: string;
  expandAllOnChange?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  showAbstract: true,
  showAdd: false,
  showRemove: false,
  title: 'Artikel',
  emptyMessage: 'Keine Ergebnisse vorhanden.',
  expandAllOnChange: false,
});

const emit = defineEmits<{
  add: [paper: Paper];
  remove: [paper: Paper];
}>();

// Store IDs of expanded panels
const expanded = ref<(number | string)[]>([]);

// Memoize paper IDs to avoid recalculating on every render
const paperIds = computed(() => props.papers.map((p) => p.paper_id));

// Auto-expand logic with performance optimization
watch(
  () => props.papers,
  (newPapers) => {
    if (props.expandAllOnChange && newPapers.length > 0) {
      // Use nextTick to avoid blocking UI updates
      nextTick(() => {
        expanded.value = newPapers.map((p) => p.paper_id);
      });
    } else if (!props.expandAllOnChange) {
      // Clear expanded panels when papers change (unless auto-expand is enabled)
      // This prevents stale panel states
      expanded.value = expanded.value.filter((id) =>
        newPapers.some((p) => p.paper_id === id)
      );
    }
  },
  { immediate: props.expandAllOnChange }
);

// Event handlers
const handleAdd = (paper: Paper) => emit('add', paper);
const handleRemove = (paper: Paper) => emit('remove', paper);
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
          :show-remove="showRemove"
          @add="handleAdd"
          @remove="handleRemove"
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
  /* Optimize rendering by promoting to own layer */
  will-change: auto;
}

.paper-panel {
  /* Smooth transitions */
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
