<script setup lang="ts">
import { computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { VAlert, VProgressLinear } from 'vuetify/components';
import ProjectDetailsSection from '@/components/organisms/project/ProjectDetailsSection.vue';
import type { Paper } from '@/types/content';
import { useProjectsService } from '@/services/projectsService';

const route = useRoute();
const projectId = computed(() => Number(route.params.projectId));

const {
  selectedProject,
  selectProject,
  renameProject,
  removePaperFromProject,
  loading,
} = useProjectsService();

const papers = computed<Paper[]>(() => {
  if (!selectedProject.value) return [];
  return selectedProject.value.papers.map((p) => ({
    paper_id: p.paper_id,
    title: p.title,
    author: p.authors ? Object.values(p.authors).join(', ') : '',
    year: p.published_at ? new Date(p.published_at).getFullYear() : 0,
    abstract: p.abstract ?? undefined,
  }));
});

const projectName = computed(() => selectedProject.value?.project.project_name ?? '');

const loadProject = async () => {
  if (Number.isFinite(projectId.value)) {
    await selectProject(projectId.value);
  }
};

onMounted(loadProject);
watch(
  () => route.params.projectId,
  () => {
    loadProject();
  },
);

const handleRenameProject = async (newName: string) => {
  if (!projectId.value) return;
  await renameProject(projectId.value, newName);
};

const handleRemovePaper = async (paper: Paper) => {
  if (!paper.paper_id || !projectId.value) return;
  await removePaperFromProject(projectId.value, paper.paper_id);
};
</script>

<template>
  <div class="project-page">
    <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-4" />

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
