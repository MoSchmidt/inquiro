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
import { ChevronDown, Copy, Eye, FolderPlus, MoreHorizontal, RotateCcw, Sparkles } from 'lucide-vue-next';
import { computed, ref, withDefaults } from 'vue';
import type { Paper, PaperMenuOption } from '@/types/content';
import ActionMenu, { type ActionMenuItem } from '@/components/molecules/ActionMenu.vue';
import { usePaperSummariesStore } from '@/stores/paperSummaries';
import FormattedMarkdown from '@/components/atoms/FormattedMarkdown.vue';

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

const isMenuOpen = ref(false);

const emit = defineEmits<{
  (e: 'add', paper: Paper): void;
  (e: 'menu-select', payload: { option: PaperMenuOption; paper: Paper }): void;
  (e: 'view', paper: Paper): void;
}>();

// ----- summarise paper -----
const summariesStore = usePaperSummariesStore();

const entry = computed(() => summariesStore.entry(props.paper.paper_id));
const isLoading = computed(() => entry.value.status === 'loading');
const isError = computed(() => entry.value.status === 'error');
const summaryMarkdown = computed(() => entry.value.summaryMarkdown ?? '');
const showSummaryChip = computed(() => summariesStore.hasSummary(props.paper.paper_id));

const regenerate = () => summariesStore.summarise(props.paper.paper_id, { force: true });

const copySummary = async () => {
  if (!summaryMarkdown.value) return;
  try {
    await navigator.clipboard.writeText(summaryMarkdown.value);
  } catch {
    // ignore
  }
};

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

          <!-- Summary chip -->
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

        <ActionMenu
            v-if="transformedMenuOptions.length"
            :items="transformedMenuOptions"
        />
        <v-menu
          v-if="menuOptions && menuOptions.length"
          v-model="isMenuOpen"
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
              @click.stop="
                isMenuOpen=false;
                emit('menu-select', { option, paper })
              "
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

        <div v-else class="summary-content">
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

.expand-icon { transition: transform 0.2s ease; }
.expand-icon--expanded { transform: rotate(180deg); }

.action-buttons :deep(.v-btn) { margin-left: 0; }
.action-buttons :deep(.v-btn) {
  margin-left: 0;
}

.summary-content {
  line-height: 1.55;
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.04);
  border: 1px solid rgba(15, 23, 42, 0.06);
}
</style>