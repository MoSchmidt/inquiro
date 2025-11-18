<script setup lang="ts">
import { VCard, VCardTitle, VCardText, VTable, VIcon, VRow, VCol } from 'vuetify/components';
import { FileText, ExternalLink } from 'lucide-vue-next';
import { Paper } from './types'; // Importiere den Typ

const props = defineProps<{
  query: string;
  outputs: Paper[];
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
      <h3 class="text-h6 mb-4">Generierte Artikel ({{ outputs.length }})</h3>
      <v-card flat class="overflow-hidden">
        <v-table density="default">
          <thead>
          <tr>
            <th class="text-left w-40">Titel</th>
            <th class="text-left w-30">Autor</th>
            <th class="text-left w-15">Jahr</th>
            <th class="text-left w-15">URL</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="(paper, index) in outputs" :key="index">
            <td>{{ paper.title }}</td>
            <td class="text-medium-emphasis">{{ paper.author }}</td>
            <td>{{ paper.year }}</td>
            <td>
              <a
                  :href="paper.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-decoration-none text-blue-darken-2 d-inline-flex align-center"
              >
                Link
                <v-icon :icon="ExternalLink" size="14" class="ms-1"></v-icon>
              </a>
            </td>
          </tr>
          </tbody>
        </v-table>
      </v-card>
    </div>

    <div v-if="outputs.length === 0" class="text-center py-12">
      <p class="text-medium-emphasis">Noch keine Ergebnisse generiert</p>
    </div>
  </v-container>
</template>

<style scoped>
.bg-blue-lighten-5 {
  background-color: #e9f2ff !important; /* Lighter blue */
}
.border-sm {
  border: 1px solid #BBDEFB; /* Light blue border */
}
.w-40 { width: 40%; }
.w-30 { width: 30%; }
.w-15 { width: 15%; }
</style>