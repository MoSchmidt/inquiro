<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { VAlert, VProgressLinear, VDialog, VCard, VCardTitle, VCardText, VSelect, VCardActions, VSpacer, VBtn } from 'vuetify/components';

import SearchResultsSection from '@/components/organisms/search/SearchResultsSection.vue';
import PdfViewerDialog from '@/components/organisms/pdf/PdfViewerDialog.vue';
import type { Paper } from '@/types/content';

import { searchPapers, searchPapersByPdf } from '@/services/search';
import { useAuthStore } from '@/stores/auth';
import { useProjectsStore } from '@/stores/projects';
import { useSearchStore } from '@/stores/search';
import { mapSearchResponseToPapers } from '@/mappers/paper-mapper';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const projectsStore = useProjectsStore();
const searchStore = useSearchStore();

// ----- state -----
const currentQueryText = ref('');
const currentFile = ref<File | null>(null);

const outputs = ref<Paper[]>([]);
const isLoading = ref(false);
const errorMessage = ref<string | null>(null);

// Dialog states
const addToProjectDialogOpen = ref(false);
const paperToAdd = ref<Paper | null>(null);
const selectedProjectIdForAdd = ref<number | null>(null);
const pdfViewerOpen = ref(false);
const pdfPaperId = ref<number | null>(null);
const pdfPaperTitle = ref('');

// ----- derived state -----
const isAuthenticated = computed(() => authStore.isAuthenticated);
const projects = computed(() => projectsStore.projects);
const projectOptions = computed(() => projectsStore.projects);

// ----- lifecycle -----

onMounted(async () => {
  if (isAuthenticated.value) {
    await projectsStore.loadProjects();
  }
  await initializeSearch();
});

// Watcher: Handles Search when URL changes (e.g. from Home -> Search or Search -> Search)
watch(() => route.query.q, async (newQuery) => {
  // We allow the watcher to run even if query text is same,
  // IF there is a staged file waiting in the store.
  if (newQuery !== currentQueryText.value || searchStore.stagedFile) {
    await initializeSearch();
  }
});

// ----- search logic -----

const initializeSearch = async () => {
  // 1. Check Pinia store for a File (passed from Home)
  const storedFile = searchStore.stagedFile;

  // 2. Check URL query for text
  const queryParam = route.query.q?.toString() || '';

  // [FIX] If we have neither, CLEAR the results instead of just returning.
  if (!queryParam && !storedFile) {
    outputs.value = [];
    currentQueryText.value = '';
    currentFile.value = null;
    errorMessage.value = null;
    return;
  }

  // 3. Consume the file from the store
  if (storedFile) {
    searchStore.setStagedFile(null);
  }

  await performSearch(queryParam, storedFile || null);
};

const performSearch = async (query: string, file: File | null) => {
  // [FIX] Guard clause: If no query AND no file, do not call API.
  if (!query.trim() && !file) {
    isLoading.value = false;
    return;
  }

  currentQueryText.value = query;
  currentFile.value = file;

  outputs.value = [];
  errorMessage.value = null;
  isLoading.value = true;

  try {
    let response;
    if (file) {
      // Pass undefined if query is empty string, assuming your service handles that
      response = await searchPapersByPdf(file, query || undefined);
    } else {
      response = await searchPapers(query);
    }
    outputs.value = mapSearchResponseToPapers(response);
  } catch (err) {
    console.error('Search failed', err);
    errorMessage.value = 'Search failed.';
  } finally {
    isLoading.value = false;
  }
};

// Handle new search from within the Results Page (The Search Bar at the top)
const handleUpdateQuery = async (payload: { query: string; file: File | null } | string) => {
  const query = typeof payload === 'string' ? payload : payload.query;
  const file = typeof payload !== 'string' && payload.file ? payload.file : null;

  // 1. If we have a file, put it in the Store
  if (file) {
    searchStore.setStagedFile(file);
  }

  const isTextSame = query === currentQueryText.value;

  // 2. Update URL
  // This usually triggers the `watch` above ^
  await router.push({ query: { q: query } });

  // 3. Edge Case: If the text is exactly the same, the URL didn't change,
  // so the Watcher won't fire. We must manually trigger the search.
  if (isTextSame && file) {
    await initializeSearch();
  }
};

// ----- add-to-project & view logic (unchanged) -----

const handleAddFromSearch = (paper: Paper) => {
  if (!isAuthenticated.value || !projects.value.length) return;
  paperToAdd.value = paper;
  selectedProjectIdForAdd.value = projects.value[0]?.project_id ?? null;
  addToProjectDialogOpen.value = true;
};

const confirmAddToProject = async () => {
  if (!paperToAdd.value?.paper_id || !selectedProjectIdForAdd.value) {
    addToProjectDialogOpen.value = false;
    return;
  }
  await projectsStore.addPaper(selectedProjectIdForAdd.value, paperToAdd.value.paper_id);
  addToProjectDialogOpen.value = false;
  paperToAdd.value = null;
};

const handleViewPaper = (paper: Paper) => {
  pdfPaperId.value = paper.paper_id;
  pdfPaperTitle.value = paper.title;
  pdfViewerOpen.value = true;
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

    <SearchResultsSection
        :query="currentQueryText"
        :file="currentFile"
        :outputs="outputs"
        :show-abstract="true"
        :show-add="isAuthenticated"
        @add="handleAddFromSearch"
        @view="handleViewPaper"
        @update-query="handleUpdateQuery"
    />

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

    <PdfViewerDialog
        :open="pdfViewerOpen"
        :paper-id="pdfPaperId"
        :paper-title="pdfPaperTitle"
        @close="pdfViewerOpen = false"
    />
  </div>
</template>

<style scoped>
.search-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 8px;
}
</style>