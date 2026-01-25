<script setup lang="ts">
import {
  VBtn,
  VExpansionPanelText,
  VExpansionPanelTitle,
  VIcon,
  VChip,
  VTooltip,
  VDivider,
  VAlert,
  VSkeletonLoader
} from 'vuetify/components';
import { Copy, Eye, FolderPlus, RotateCcw, Sparkles } from 'lucide-vue-next';
import { computed, withDefaults } from 'vue';
import type { ActionMenuItem } from '@/types/ui';
import ActionMenu from '@/components/molecules/ActionMenu.vue';
import { usePaperSummariesStore } from '@/stores/paperSummaries';
import type { Paper } from '@/types/content';
import FormattedMarkdown from '@/components/atoms/FormattedMarkdown.vue';
import ExpansionChevron from '@/components/atoms/ExpansionChevron.vue';

const props = withDefaults(
    defineProps<{
      paper: Paper;
      showAbstract?: boolean;
      showAdd?: boolean;
      actions?: ActionMenuItem[];
      queryContext?: string;
    }>(),
    {
      showAbstract: true,
      showAdd: false,
      actions: () => [],
      queryContext: '',
    }
);

const emit = defineEmits<{
  (e: 'add', paper: Paper): void;
  (e: 'view', paper: Paper): void;
}>();

// ----- summarise paper -----
const summariesStore = usePaperSummariesStore();

const entry = computed(() => summariesStore.entry(props.paper.paper_id));
const isLoading = computed(() => entry.value.status === 'loading');
const isError = computed(() => entry.value.status === 'error');
const summaryMarkdown = computed(() => entry.value.summaryMarkdown ?? '');
const showSummaryChip = computed(() => summariesStore.hasSummary(props.paper.paper_id));

const regenerate = () => summariesStore.summarise(props.paper.paper_id, { force: true, query: props.queryContext });

const copySummary = async () => {
  if (!summaryMarkdown.value) return;
  try {
    await navigator.clipboard.writeText(summaryMarkdown.value);
  } catch {
    // ignore
  }
};
</script>

<template>
  <v-expansion-panel-title v-slot="{ expanded }">
    <div class="paper-header w-100">
      <!-- Expand icon -->
      <div class="expand-icon-wrapper flex items-center justify-center">
        <ExpansionChevron :expanded="expanded" />
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

          <v-chip
              v-if="showSummaryChip"
              size="x-small"
              class="ms-2"
              variant="tonal"
          >
            <v-icon :icon="Sparkles" size="14" class="me-1" />
            Summary
          </v-chip>
        </div>

        <div class="text-body-2 text-medium-emphasis paper-meta">
          <span v-if="paper.author">{{ paper.author }}</span>
        </div>
      </div>

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
          <v-tooltip activator="parent" location="top">Add to Project</v-tooltip>
        </v-btn>

        <ActionMenu
            v-if="actions.length"
            :items="actions"
        />
      </div>
    </div>
  </v-expansion-panel-title>

  <v-expansion-panel-text>
    <div class="text-body-2 text-medium-emphasis mb-3 paper-abstract">
      <span v-if="showAbstract && paper.abstract"> {{ paper.abstract }} </span>
      <span v-else class="text-disabled"> No abstract available. </span>
    </div>

    <template v-if="isLoading || isError || summaryMarkdown">
      <v-divider class="my-4" />

      <div class="summary-block">
        <div class="d-flex align-center justify-space-between mb-2">
          <div class="d-flex align-center">
            <v-icon :icon="Sparkles" size="18" class="me-2" />
            <div class="text-subtitle-2 font-weight-medium">AI Summary</div>
          </div>

          <div class="d-flex align-center" style="gap: 6px;">
            <v-btn v-if="summaryMarkdown" size="small" variant="text" @click="copySummary">
              <v-icon :icon="Copy" size="16" class="me-1" />
              Copy
            </v-btn>

            <v-btn
                v-if="summaryMarkdown"
                size="small"
                variant="text"
                :disabled="isLoading"
                @click="regenerate"
            >
              <v-icon :icon="RotateCcw" size="16" class="me-1" />
              Regenerate
            </v-btn>
          </div>
        </div>

        <v-alert v-if="isError" type="error" variant="tonal" class="mb-3">
          {{ entry.error || "Failed to summarise paper." }}
          <template #append>
            <v-btn size="small" variant="text" @click="regenerate">Retry</v-btn>
          </template>
        </v-alert>

        <v-skeleton-loader v-if="isLoading" type="paragraph, paragraph, paragraph" />

        <div v-else>
          <FormattedMarkdown :markdown="summaryMarkdown" />
        </div>
      </div>
    </template>
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

.action-buttons :deep(.v-btn) {
  margin-left: 0;
}
</style>
