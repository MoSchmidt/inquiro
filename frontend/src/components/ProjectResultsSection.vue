<script setup lang="ts">
import {
  VCard,
  VCardText,
  VIcon,
  VExpansionPanels,
  VExpansionPanel,
  VExpansionPanelTitle,
  VExpansionPanelText,
  VBtn,
} from 'vuetify/components';
import { FileText, ExternalLink, Trash2 } from 'lucide-vue-next';
import type { Paper } from './types';

const props = defineProps<{
  projectName: string;
  papers: Paper[];
  showAbstract?: boolean;
}>();

const emit = defineEmits<{
  (e: 'remove', paper: Paper): void;
}>();
</script>

<template>
  <v-container class="py-6" style="max-width: 1200px;">
    <v-card flat class="mb-6 pa-4 project-header-card">
      <v-card-text class="pa-0">
        <div class="d-flex align-center mb-2">
          <div class="project-icon d-flex align-center justify-center me-3">
            <v-icon :icon="FileText" size="20" />
          </div>
          <h1 class="project-title">
            {{ projectName }}
          </h1>
        </div>
        <p class="text-caption text-medium-emphasis">
          {{ papers.length }} saved papers
        </p>
      </v-card-text>
    </v-card>

    <div>
      <h3 class="text-h6 mb-4">Articles ({{ papers.length }})</h3>

      <v-expansion-panels v-if="papers.length" multiple class="paper-panels">
        <v-expansion-panel
          v-for="(paper, index) in papers"
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
              <div class="d-flex align-center mt-2 mt-sm-0">
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="error"
                  @click.stop="emit('remove', paper)"
                >
                  <v-icon :icon="Trash2" size="16" />
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

      <div v-else class="text-center py-12">
        <p class="text-medium-emphasis">This project has no saved papers yet.</p>
      </div>
    </div>
  </v-container>
</template>

<style scoped>
.project-header-card {
  border-radius: 0;
  border: none;
  border-bottom: 1px solid rgba(148, 163, 184, 0.45);
  background: transparent;
}

.project-icon {
  width: 40px;
  height: 40px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.04);
  color: #1f2937;
}

.project-title {
  font-size: 1.8rem;
  font-weight: 650;
  letter-spacing: 0.02em;
}

.paper-panels {
  gap: 12px;
}

.paper-panel {
  border-radius: 12px !important;
  border: 1px solid var(--paper-panel-border);
  background: linear-gradient(135deg, #ffffff, #f8fafc);
  transition: box-shadow 0.18s ease, transform 0.18s ease, border-color 0.18s ease;
}

.paper-panel:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 25px var(--paper-panel-hover-shadow);
  border-color: var(--paper-panel-hover-border);
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


