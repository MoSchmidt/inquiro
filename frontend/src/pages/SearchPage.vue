<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import {
  VAlert,
  VBtn,
  VCard,
  VCardActions,
  VCardText,
  VCardTitle,
  VDialog,
  VProgressLinear,
  VSelect,
  VSpacer,
} from 'vuetify/components';

import SearchInputSection from '@/components/organisms/search/SearchInputSection.vue';
import SearchResultsSection from '@/components/organisms/search/SearchResultsSection.vue';
import type { Paper } from '@/types/content';

import { searchPapers } from '@/services/search';
import { useAuthStore } from '@/stores/auth';
import { useProjectsStore } from '@/stores/projects';

const authStore = useAuthStore();
const projectsStore = useProjectsStore();

const currentQuery = ref<string | null>(null);
const outputs = ref<Paper[]>([]);
const isLoading = ref(false);
const errorMessage = ref<string | null>(null);

// add-to-project dialog state
const addToProjectDialogOpen = ref(false);
const paperToAdd = ref<Paper | null>(null);
const selectedProjectIdForAdd = ref<number | null>(null);

// derived state
const isAuthenticated = computed(() => authStore.isAuthenticated);
const projects = computed(() => projectsStore.projects);
const projectOptions = computed(() => projectsStore.projects);

onMounted(() => {
  if (isAuthenticated.value) {
    projectsStore.loadProjects();
  }
});

// ----- search flow -----

const handleSubmitQuery = async (query: string) => {
  currentQuery.value = query;
  outputs.value = [];
  errorMessage.value = null;
  isLoading.value = true;

  try {
    const response = await searchPapers(query);
    outputs.value = response.papers.map((p) => ({
      paper_id: p.paper_id,
      title: p.title,
      author: p.authors ? Object.values(p.authors).join(', ') : '',
      year: p.published_at ? new Date(p.published_at).getFullYear() : 0,
      abstract: p.abstract ?? undefined,
    }));
  } catch (err) {
    console.error('Search failed', err);
    errorMessage.value = 'Search failed.';
  } finally {
    isLoading.value = false;
  }
};

// ----- add-from-search flow -----

const handleAddFromSearch = (paper: Paper) => {
  if (!isAuthenticated.value || !projects.value.length) {
    return;
  }

  paperToAdd.value = paper;
  selectedProjectIdForAdd.value = projects.value[0]?.project_id ?? null;
  addToProjectDialogOpen.value = true;
};

const confirmAddToProject = async () => {
  if (!paperToAdd.value?.paper_id || !selectedProjectIdForAdd.value) {
    addToProjectDialogOpen.value = false;
    return;
  }

  await projectsStore.addPaper(
    selectedProjectIdForAdd.value,
    paperToAdd.value.paper_id
  );

  addToProjectDialogOpen.value = false;
  paperToAdd.value = null;
};
</script>

<template>
  <div class="search-page">
    <div v-if="isLoading" class="mb-4">
      <v-progress-linear indeterminate color="primary" />
    </div>

    <v-alert v-if="errorMessage" type="error" class="mb-4">
      {{ errorMessage }}
    </v-alert>

    <div v-if="!currentQuery">
      <SearchInputSection @submit="handleSubmitQuery" />
    </div>
    <div v-else>
      <SearchResultsSection
        :query="currentQuery || ''"
        :outputs="outputs"
        :show-abstract="true"
        :show-add="isAuthenticated"
        @add="handleAddFromSearch"
        @update-query="handleSubmitQuery"
      />
    </div>

    <v-dialog v-model="addToProjectDialogOpen" max-width="500">
      <v-card>
        <v-card-title class="text-h5"> Add paper to project </v-card-title>
        <v-card-text>
          <p class="mb-4 text-medium-emphasis">
            Choose a project to add this paper to.
          </p>
          <v-select
            v-model="selectedProjectIdForAdd"
            :items="projectOptions"
            item-title="project_name"
            item-value="project_id"
            label="Project"
            variant="outlined"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="addToProjectDialogOpen = false">
            Cancel
          </v-btn>
          <v-btn color="primary" @click="confirmAddToProject"> Add </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
.search-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 8px;
}
</style>
