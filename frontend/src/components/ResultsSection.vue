<script setup lang="ts">
import {computed, ref, watch} from 'vue';
import {
  VCard,
  VCardText,
  VIcon,
  VBtn,
  VTextField,
  VExpansionPanels,
  VExpansionPanel,
  VExpansionPanelTitle,
  VExpansionPanelText,
} from 'vuetify/components';
import { FileText, ExternalLink, FolderPlus, Edit3 } from 'lucide-vue-next';
import type { Paper } from './types';

const props = defineProps<{
  query: string;
  outputs: Paper[];
  showAbstract?: boolean;
  showAdd?: boolean;
}>();

const emit = defineEmits<{
  (e: 'add', paper: Paper): void;
  (e: 'updateQuery', newQuery: string): void;
}>();

const expanded = ref<number[]>([]);
const editableQuery = ref(props.query);
const isQueryChanged = computed(() => editableQuery.value.trim() !== props.query.trim());
const handleQueryUpdate = () => {
  if (editableQuery.value.trim()) {
    emit('updateQuery', editableQuery.value.trim());
  }
};
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
    <v-container class="results-section">
      <v-card flat class="mb-8 pa-4 bg-blue-lighten-5 border-sm">
        <v-card-text class="d-flex align-start pa-0">
          <v-icon :icon="FileText" color="blue-darken-2" class="mt-1 me-3"></v-icon>
          <div class="flex-grow-1">
            <v-text-field
                v-model="editableQuery"
                label="Ihre Abfrage"
                variant="outlined"
                dense
                class="mb-2"
            ></v-text-field>
            <v-btn
                v-if="isQueryChanged"
                color="primary"
                variant="outlined"
                size="small"
                @click="handleQueryUpdate">
              <v-icon :icon="Edit3" start size="18"/>
              Abfrage aktualisieren
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
      <h3 class="text-h6 mb-4">Artikel ({{ outputs.length }})</h3>
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
                Kein Abstract vorhanden.
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
                Zum Paper
                <v-icon :icon="ExternalLink" size="14" class="ms-1"></v-icon>
              </a>
              <span v-else class="text-disabled">Keine URL verfügbar.</span>
            </div>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>

    <div v-if="outputs.length === 0" class="text-center py-12">
      <p class="text-medium-emphasis">Noch keine Ergebnisse vorhanden</p>
    </div>
  </v-container>
</template>

<style scoped>
.bg-blue-lighten-5 {
  background-color: var(--blue-lighten-5) !important;
}
.border-sm {
  border: 1px solid var(--border-sm-color-result);
}

.paper-panels {
  gap: 12px;
}

.paper-panel {
  border-radius: 12px !important;
  border: 1px solid var(--paper-panel-border);
  background: linear-gradient(135deg, #ffffff, #f9fafb);
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