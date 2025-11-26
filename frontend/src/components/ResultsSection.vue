<script setup lang="ts">
import { VCard, VCardTitle, VCardText, VTable, VIcon, VBtn } from 'vuetify/components';
import { FileText, ExternalLink, Trash2 } from 'lucide-vue-next';
import type { Paper } from './types';

const props = defineProps<{
  query: string;
  outputs: Paper[];
  showAbstract?: boolean;
  showActions?: boolean;
}>();

const emit = defineEmits<{
  (e: 'remove', paper: Paper): void;
}>();
</script>

<template>
  <v-container class="py-6" style="max-width: 1200px;">
    <v-card flat class="mb-8 pa-4 bg-blue-lighten-5 border-sm">
      <v-card-text class="d-flex align-start pa-0">
        <v-icon :icon="FileText" color="blue-darken-2" class="mt-1 me-3"></v-icon>
        <div>
          <h3 class="text-h6 text-blue-darken-4 mb-2">Ihre Abfrage</h3>
          <p class="text-blue-darken-3">{{ query }}</p>
        </div>
      </v-card-text>
    </v-card>

    <div>
      <h3 class="text-h6 mb-4">Artikel ({{ outputs.length }})</h3>
      <v-card flat>
        <v-table
          density="default"
          fixed-header
          height="400px"
        >
          <thead>
            <tr>
              <th class="text-left w-35">Titel</th>
              <th class="text-left w-15">Autor</th>
              <th class="text-left w-10">Jahr</th>
              <th class="text-left w-25">Abstract</th>
              <th class="text-left w-10">URL</th>
              <th v-if="showActions" class="text-left w-5">Aktion</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(paper, index) in outputs" :key="index">
              <td>{{ paper.title }}</td>
              <td class="text-medium-emphasis">{{ paper.author }}</td>
              <td>{{ paper.year }}</td>
              <td>
                <div v-if="showAbstract && paper.abstract" class="text-body-2 text-medium-emphasis">
                  {{ paper.abstract }}
                </div>
                <span v-else class="text-disabled">–</span>
              </td>
              <td>
                <a
                  v-if="paper.url"
                  :href="paper.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-decoration-none text-blue-darken-2 d-inline-flex align-center"
                >
                  Link
                  <v-icon :icon="ExternalLink" size="14" class="ms-1"></v-icon>
                </a>
                <span v-else class="text-disabled">–</span>
              </td>
              <td v-if="showActions">
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="error"
                  @click="emit('remove', paper)"
                >
                  <v-icon :icon="Trash2" size="16" />
                </v-btn>
              </td>
            </tr>
          </tbody>
        </v-table>
      </v-card>
    </div>

    <div v-if="outputs.length === 0" class="text-center py-12">
      <p class="text-medium-emphasis">Noch keine Ergebnisse vorhanden</p>
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
</style>