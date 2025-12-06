<script setup lang="ts">
import { computed, ref } from 'vue';
import {
  VCard,
  VCardText,
  VIcon,
  VContainer,
  VBtn,
  VTextField,
} from 'vuetify/components';
import { FileText, Edit3 } from 'lucide-vue-next';
import PaperList from '@/components/molecules/PaperList.vue';
import type { Paper } from '@/types/content';

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

const editableQuery = ref(props.query);
const isQueryChanged = computed(() => editableQuery.value.trim() !== props.query.trim());
const handleQueryUpdate = () => {
  if (editableQuery.value.trim()) {
    emit('updateQuery', editableQuery.value.trim());
  }
};
</script>

<template>
    <v-container class="results-section">
      <v-card flat class="mb-8 pa-4 bg-blue-lighten-5 border-sm">
        <v-card-text class="d-flex align-start pa-0">
          <v-icon :icon="FileText" color="blue-darken-2" class="mt-1 me-3"></v-icon>
          <div class="flex-grow-1">
            <v-text-field
                v-model="editableQuery"
                label="Your Query"
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
              Update query
            </v-btn>
          </div>
        </v-card-text>
      </v-card>

    <PaperList
      :papers="outputs"
      :show-abstract="showAbstract"
      :show-add="showAdd"
      title="Articles"
      empty-message="No results yet"
      :expand-all-on-change="true"
      @add="paper => emit('add', paper)"
    />
  </v-container>
</template>

<style scoped>
.bg-blue-lighten-5 {
  background-color: var(--blue-lighten-5) !important;
}
.border-sm {
  border: 1px solid var(--border-sm-color-result);
}
</style>