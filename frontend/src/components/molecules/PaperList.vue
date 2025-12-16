<script setup lang="ts">
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
  withDefaults,
} from 'vue';
import {
  VBtn,
  VExpansionPanel,
  VExpansionPanels,
  VIcon,
  VTextField,
} from 'vuetify/components';
import type { Paper, PaperMenuOption } from '@/types/content';
import PaperCard from '@/components/atoms/PaperCard.vue';
import { ArrowUp, Search, X } from 'lucide-vue-next';
import { useScrollToTop } from '@/composables/useScrollToTop';
import { usePaperSummariesStore } from '@/stores/paperSummaries';

interface Props {
  papers: Paper[];
  showAbstract?: boolean;
  showAdd?: boolean;
  title?: string;
  emptyMessage?: string;
  expandAllOnChange?: boolean;
  menuOptions?: PaperMenuOption[];
  searchContext?: string;
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
  view: [paper: Paper];
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
    searchQuery.value = value?.trim().toLowerCase() ?? '';
  }, 300);
});

onBeforeUnmount(() => {
  window.clearTimeout(searchDebounce);
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
    if (props.expandAllOnChange && newPapers.length) {
      nextTick(() => {
        expanded.value = newPapers.map((p) => p.paper_id);
      });
    } else {
      expanded.value = expanded.value.filter((id) =>
        newPapers.some((p) => p.paper_id === id)
      );
    }
  },
  { immediate: props.expandAllOnChange }
);

// ----- floating "back to top" button -----

const searchFieldRef = ref<HTMLElement | null>(null);
const showScrollTop = ref(false);

let observer: IntersectionObserver | null = null;

onMounted(() => {
  if (!searchFieldRef.value || !('IntersectionObserver' in window)) return;

  observer = new IntersectionObserver(
    ([entry]) => {
      // show button when search field is NOT visible
      showScrollTop.value = !entry.isIntersecting;
    },
    { threshold: 0 }
  );

  observer.observe(searchFieldRef.value);
});

onBeforeUnmount(() => {
  observer?.disconnect();
});

const { scrollToTop } = useScrollToTop();

const handleScrollToTop = () => {
  scrollToTop(searchFieldRef.value);
};

// ----- summarise paper -----
watch(() => props.papers, (newPapers) => {
  if (props.expandAllOnChange && newPapers.length > 0) {
    nextTick(() => {
      expanded.value = newPapers.map((p) => p.paper_id);
    });
  } else if (!props.expandAllOnChange) {
    expanded.value = expanded.value.filter((id) => newPapers.some((p) => p.paper_id === id));
  }
}, { immediate: props.expandAllOnChange });

const summariesStore = usePaperSummariesStore();

// ----- events -----

const handleAdd = (paper: Paper) => emit('add', paper);
const handleMenuSelect = async (payload: { option: PaperMenuOption; paper: Paper }) => {
  if (payload.option.value === 'summarise') {
    const queryToUse = props.searchContext || "";
    await summariesStore.summarise(payload.paper.paper_id, { query: queryToUse });

    if (!expanded.value.includes(payload.paper.paper_id)) {
      expanded.value = [...expanded.value, payload.paper.paper_id];
    }
    return;
  }

  emit('menu-select', payload);
};
const handleView = (paper: Paper) => emit('view', paper);
</script>

<template>
  <section class="paper-list">
    <div ref="searchFieldRef">
      <v-text-field
        v-model="rawSearch"
        placeholder="Search papers"
        variant="outlined"
        clearable
        :clear-icon="X"
        class="mt-4"
        aria-label="Search research papers"
      >
        <template #prepend-inner>
          <v-icon :icon="Search" size="18" />
        </template>
      </v-text-field>
    </div>

    <h3 class="mb-4">
      {{ title }}
      <span class="text-medium-emphasis"> ({{ filteredPapers.length }}) </span>
    </h3>

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
            @view="handleView"
        />
      </v-expansion-panel>
    </v-expansion-panels>

    <div v-else class="empty-state">
      <p class="text-medium-emphasis">
        {{ searchQuery ? 'No papers match your search.' : emptyMessage }}
      </p>
    </div>

    <!-- floating back-to-top button -->
    <v-btn
      v-if="showScrollTop"
      class="scroll-top-btn"
      icon
      variant="tonal"
      size="small"
      elevation="1"
      :ripple="false"
      aria-label="Scroll back to top"
      @click="handleScrollToTop"
    >
      <v-icon :icon="ArrowUp" size="18" />
      <v-tooltip activator="parent" location="left"> Back to top </v-tooltip>
    </v-btn>
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

.scroll-top-btn {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
  opacity: 0.85;
}

.scroll-top-btn:hover {
  opacity: 1;
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
