<script setup lang="ts">
import { ref, watch } from 'vue';
import {
  VCard,
  VCardTitle,
  VCardText,
  VIcon,
  VBtn,
  VExpansionPanels,
  VExpansionPanel,
  VExpansionPanelTitle,
  VExpansionPanelText,
} from 'vuetify/components';
import { FileText, ExternalLink, FolderPlus } from 'lucide-vue-next';
import type { Paper } from './types';

const props = defineProps<{
  query: string;
  outputs: Paper[];
  showAbstract?: boolean;
  showAdd?: boolean;
}>();

const emit = defineEmits<{
  (e: 'add', paper: Paper): void;
}>();

const expanded = ref<number[]>([]);

watch(
  () => props.outputs,
  (newOutputs) => {
    // Expand all panels whenever a new result set arrives
    expanded.value = newOutputs.map((_, index) => index);
  },
  { immediate: true },
);
</script>

<template>
  <v-container class="py-6" style="max-width: 1200px;">
    <v-card flat class="mb-8 pa-4 bg-blue-lighten-5 border-sm">
      <v-card-text class="d-flex align-start pa-0">
        <v-icon :icon="FileText" color="blue-darken-2" class="mt-1 me-3"></v-icon>
        <div>
          <h3 class="text-h6 text-blue-darken-4 mb-2">Your Query</h3>
          <p class="text-blue-darken-3">{{ query }}</p>
        </div>
      </v-card-text>
    </v-card>

    <div>
      <h3 class="text-h6 mb-4">Articles ({{ outputs.length }})</h3>
      <v-expansion-panels v-if="outputs.length" v-model="expanded" multiple class="paper-panels">
        <v-expansion-panel
          v-for="(paper, index) in outputs"
          :key="index"
          elevation="1"
          class="mb-3 paper-panel"
        >
          <v-expansion-panel-title>
            <div class="paper-header d-flex flex-column flex-sm-row w-100">
              <div class="flex-grow-1 me-sm-4">
                <div class="text-subtitle-1 font-weight-medium paper-title text-truncate">
                  {{ paper.title }}
                </div>
                <div class="text-body-2 text-medium-emphasis paper-meta">
                  <span v-if="paper.author">{{ paper.author }}</span>
                  <span v-if="paper.author && paper.year">&nbsp;•&nbsp;</span>
                  <span v-if="paper.year">{{ paper.year }}</span>
                </div>
              </div>
              <div class="d-flex align-center mt-2 mt-sm-0" v-if="showAdd">
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="primary"
                  @click.stop="emit('add', paper)"
                >
                  <v-icon :icon="FolderPlus" size="16" />
                </v-btn>
              </div>
            </div>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <div class="text-body-2 text-medium-emphasis mb-3 paper-abstract">
              <span v-if="showAbstract && paper.abstract">
                {{ paper.abstract }}
              </span>
              <span v-else class="text-disabled">
                No abstract available.
              </span>
            </div>
            <div>
              <a
                v-if="paper.url"
                :href="paper.url"
                target="_blank"
                rel="noopener noreferrer"
                class="text-decoration-none text-blue-darken-2 d-inline-flex align-center"
              >
                View paper
                <v-icon :icon="ExternalLink" size="14" class="ms-1"></v-icon>
              </a>
              <span v-else class="text-disabled">No URL available.</span>
            </div>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </div>

    <div v-if="outputs.length === 0" class="text-center py-12">
      <p class="text-medium-emphasis">No results yet</p>
    </div>
  </v-container>
</template>

<style scoped>
.bg-blue-lighten-5 {
  background-color: #e9f2ff !important;
}
.border-sm {
  border: 1px solid #BBDEFB;
}
.w-35 { width: 35%; }
.w-25 { width: 25%; }
.w-15 { width: 15%; }
.w-10 { width: 10%; }
.w-5 { width: 5%; }

.paper-panels {
  gap: 12px;
}

.paper-panel {
  border-radius: 12px !important;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: linear-gradient(135deg, #ffffff, #f9fafb);
  transition: box-shadow 0.18s ease, transform 0.18s ease, border-color 0.18s ease;
}

.paper-panel:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
  border-color: rgba(59, 130, 246, 0.35);
}

.paper-header {
  padding-right: 4px;
}

.paper-title {
  font-weight: 600;
}

.paper-meta {
  font-size: 0.85rem;
}

.paper-abstract {
  line-height: 1.5;
}
</style>