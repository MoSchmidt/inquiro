<script setup lang="ts">
import { computed, onMounted, watch, ref } from 'vue';
import { useRoute } from 'vue-router';
import { VAlert } from 'vuetify/components';

import ProjectDetailsSection from '@/components/organisms/project/ProjectDetailsSection.vue';
import PdfViewerDialog from '@/components/organisms/pdf/PdfViewerDialog.vue';
import type { Paper } from '@/types/content';
import { useProjectsStore } from '@/stores/projects';
import {useAuthStore} from "@/stores/auth";
import { mapProjectWithPapersResponseToPapers } from '@/mappers/paper-mapper';

const authStore = useAuthStore();
const route = useRoute();
const projectsStore = useProjectsStore();

const projectId = computed(() => Number(route.params.projectId));

// ----- derived state -----

const selectedProject = computed(() => projectsStore.selectedProject);

const papers = computed<Paper[]>(() => {
  if (!selectedProject.value) return [];

  return mapProjectWithPapersResponseToPapers(selectedProject.value);
});

const projectName = computed(
  () => selectedProject.value?.project.project_name ?? ''
);

// ----- PDF Viewer State -----
const pdfViewerOpen = ref(false);
const pdfPaperId = ref<number | null>(null);
const pdfPaperTitle = ref('');

// ----- lifecycle -----

const loadProject = async () => {
  if (Number.isFinite(projectId.value)) {
    await projectsStore.selectProject(projectId.value);
  }
};

onMounted(loadProject);

watch(
  () => authStore.isAuthenticated,
  (isAuth) => {
    if (isAuth && projectId.value && !projectsStore.selectedProject) {
      loadProject();
    }
  }
);

// ----- handlers -----

const handleRenameProject = async (newName: string) => {
  if (!projectId.value) return;
  await projectsStore.renameProject(projectId.value, newName);
};

const handleRemovePaper = async (paper: Paper) => {
  if (!paper.paper_id || !projectId.value) return;
  await projectsStore.removePaper(projectId.value, paper.paper_id);
};

const handleViewPaper = (paper: Paper) => {
  pdfPaperId.value = paper.paper_id;
  pdfPaperTitle.value = paper.title;
  pdfViewerOpen.value = true;
};

</script>

<template>
  <div class="project-page">
    <ProjectDetailsSection
        v-if="selectedProject"
        :project-name="projectName"
        :papers="papers"
        :show-abstract="true"
        @remove="handleRemovePaper"
        @rename="handleRenameProject"
        @view="handleViewPaper"
    />

    <v-alert v-else type="info">
      Select a project to view its saved papers.
    </v-alert>

    <PdfViewerDialog
        :open="pdfViewerOpen"
        :paper-id="pdfPaperId"
        :paper-title="pdfPaperTitle"
        @close="pdfViewerOpen = false"
    />
  </div>
</template>

<style scoped>
.project-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 8px;
}
</style>
