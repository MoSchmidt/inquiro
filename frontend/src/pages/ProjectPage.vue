<script setup lang="ts">
import { computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { VAlert } from 'vuetify/components';

import ProjectDetailsSection from '@/components/organisms/project/ProjectDetailsSection.vue';
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
    />

    <v-alert v-else type="info">
      Select a project to view its saved papers.
    </v-alert>
  </div>
</template>

<style scoped>
.project-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 8px;
}
</style>
