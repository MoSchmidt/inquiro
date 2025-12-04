<script setup lang="ts">
import { VCard, VCardText, VContainer, VIcon } from 'vuetify/components';
import { FileText } from 'lucide-vue-next';
import PaperList from '@/components/PaperList.vue';
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
</script>

<template>
  <v-container class="py-6" style="max-width: 1200px">
    <!-- Query header card stays specific to this page -->
    <v-card flat class="mb-8 pa-4 bg-blue-lighten-5 border-sm">
      <v-card-text class="d-flex align-start pa-0">
        <v-icon
          :icon="FileText"
          color="blue-darken-2"
          class="mt-1 me-3"
        ></v-icon>
        <div>
          <h3 class="text-h6 text-blue-darken-4 mb-2">Ihre Abfrage</h3>
          <p class="text-blue-darken-3">{{ query }}</p>
        </div>
      </v-card-text>
    </v-card>

    <PaperList
      :papers="outputs"
      :show-abstract="showAbstract"
      :show-add="showAdd"
      title="Artikel"
      empty-message="Noch keine Ergebnisse vorhanden"
      :expand-all-on-change="true"
      @add="paper => emit('add', paper)"
    />
  </v-container>
</template>

<style scoped>
.bg-blue-lighten-5 {
  background-color: #e9f2ff !important;
}
.border-sm {
  border: 1px solid #bbdefb;
}
</style>
