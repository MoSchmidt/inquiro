<script setup lang="ts">
import { computed, nextTick, ref, watch, withDefaults } from 'vue';
import {
  VExpansionPanel,
  VExpansionPanels,
  VTextField,
} from 'vuetify/components';
import type { Paper, PaperMenuOption } from '@/types/content';
import PaperCard from '@/components/atoms/PaperCard.vue';
import { Search, X } from 'lucide-vue-next';

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
  title: 'Articles',
  emptyMessage: 'This project has no saved papers yet.',
  expandAllOnChange: false,
  menuOptions: () => [] as PaperMenuOption[],
});

const emit = defineEmits<{
  add: [paper: Paper];
  'menu-select': [{ option: PaperMenuOption; paper: Paper }];
}>();

// ----- expansion state -----

const expanded = ref<(number | string)[]>([]);

// ----- search (debounced) -----

const rawSearch = ref('');
const searchQuery = ref('');

let searchDebounce: number | undefined;

watch(rawSearch, (value) => {
  window.clearTimeout(searchDebounce);
  searchDebounce = window.setTimeout(() => {
    if (value) {
      searchQuery.value = value.trim().toLowerCase();
    } else {
      searchQuery.value = '';
    }
  }, 300);
});

// ----- filtered papers -----

const filteredPapers = computed(() => {
  if (!searchQuery.value) return props.papers;

  return props.papers.filter((paper) => {
    const haystack = [
      paper.title,
      paper.author,
      paper.abstract,
      paper.year?.toString(),
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();

    return haystack.includes(searchQuery.value);
  });
});

// ----- keep expansion state in sync -----

watch(
  () => filteredPapers.value,
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

// ----- event handlers -----

const handleAdd = (paper: Paper) => emit('add', paper);
const handleMenuSelect = (payload: { option: PaperMenuOption; paper: Paper }) =>
  emit('menu-select', payload);
</script>

<template>
  <section class="paper-list">
    <h3 class="text-h6 mb-4">
      {{ title }}
      <span class="text-medium-emphasis"> ({{ filteredPapers.length }}) </span>
    </h3>

    <v-text-field
      v-model="rawSearch"
      placeholder="Search papers"
      variant="outlined"
      clearable
      :clear-icon="X"
      class="mb-4"
    >
      <template #prepend-inner>
        <v-icon :icon="Search" size="18" />
      </template>
    </v-text-field>

    <v-expansion-panels
      v-if="filteredPapers.length"
      v-model="expanded"
      multiple
      class="paper-panels"
      :rounded="false"
    >
      <v-expansion-panel
        v-for="paper in filteredPapers"
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
        {{ searchQuery ? 'No papers match your search.' : emptyMessage }}
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
