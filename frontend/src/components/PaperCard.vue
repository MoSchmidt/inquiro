<script setup lang="ts">
import {
  VBtn,
  VExpansionPanelText,
  VExpansionPanelTitle,
  VIcon,
} from 'vuetify/components';
import { ChevronDown, ExternalLink, FolderPlus, Trash2 } from 'lucide-vue-next';
import { withDefaults } from 'vue';
import type { Paper } from './types';

const props = withDefaults(
  defineProps<{
    paper: Paper;
    showAbstract?: boolean;
    showAdd?: boolean;
    showRemove?: boolean;
  }>(),
  {
    showAbstract: true,
    showAdd: false,
    showRemove: false,
  }
);

const emit = defineEmits<{
  (e: 'add', paper: Paper): void;
  (e: 'remove', paper: Paper): void;
}>();
</script>

<template>
  <!-- `expanded` comes from VExpansionPanel via slot props -->
  <v-expansion-panel-title v-slot="{ expanded }">
    <div class="paper-header d-flex align-center w-100">
      <!-- Expand icon on the left -->
      <div class="expand-icon-wrapper d-flex align-center justify-center me-3">
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

      <!-- Actions -->
      <div class="d-flex align-center mt-2 mt-sm-0 action-buttons">
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

        <v-btn
          v-if="showRemove"
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
      <span v-else class="text-disabled"> Kein Abstract vorhanden. </span>
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
        <v-icon :icon="ExternalLink" size="14" class="ms-1" />
      </a>
      <span v-else class="text-disabled">Keine URL verfügbar.</span>
    </div>
  </v-expansion-panel-text>
</template>

<style scoped>
.paper-header {
  padding-right: 4px;
  cursor: pointer;
}

.paper-title {
  font-weight: 600;
}

.paper-meta {
  font-size: 0.85rem;
}

/* Abstract styling */
.paper-abstract {
  line-height: 1.5;
}

/* Expand icon behaviour */
.expand-icon-wrapper {
  width: 28px;
  height: 28px;
  border-radius: 999px;
}

.expand-icon {
  transition: transform 0.18s ease;
}

.expand-icon--expanded {
  transform: rotate(180deg);
}

.action-buttons :deep(.v-btn) {
  margin-left: 4px;
}
</style>
