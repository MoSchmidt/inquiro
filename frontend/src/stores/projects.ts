import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { ProjectResponse, ProjectWithPapersResponse } from '@/api';
import {
  addPaperToProject,
  createProject,
  deleteProject,
  getProject,
  listProjects,
  removePaperFromProject,
  updateProject,
} from '@/services/projects';

export const useProjectsStore = defineStore('projects', () => {
  const projects = ref<ProjectResponse[]>([]);
  const selectedProject = ref<ProjectWithPapersResponse | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function loadProjects() {
    loading.value = true;
    error.value = null;
    try {
      projects.value = await listProjects();
    } catch (err) {
      error.value = 'Failed to load projects.';
      console.error(err)
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function selectProject(projectId: number) {
    loading.value = true;
    error.value = null;
    try {
      selectedProject.value = await getProject(projectId);
      return selectedProject.value;
    } catch (err) {
      error.value = 'Failed to load project.';
      console.error(err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createNewProject(name: string) {
    loading.value = true;
    error.value = null;
    try {
      const project = await createProject({ project_name: name });
      projects.value.unshift(project);
      return project;
    } catch (err) {
      error.value = 'Failed to create project.';
      console.error(err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function renameProject(projectId: number, newName: string) {
    loading.value = true;
    error.value = null;
    try {
      const updated = await updateProject(projectId, { project_name: newName });

      projects.value = projects.value.map((p) =>
        p.project_id === projectId ? updated : p
      );

      if (selectedProject.value?.project.project_id === projectId) {
        selectedProject.value = {
          ...selectedProject.value,
          project: updated,
        };
      }

      return updated;
    } catch (err) {
      error.value = 'Failed to update project.';
      console.error(err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteExistingProject(projectId: number) {
    loading.value = true;
    error.value = null;
    try {
      await deleteProject(projectId);

      projects.value = projects.value.filter((p) => p.project_id !== projectId);

      if (selectedProject.value?.project.project_id === projectId) {
        selectedProject.value = null;
      }
    } catch (err) {
      error.value = 'Failed to delete project.';
      console.error(err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function addPaper(projectId: number, paperId: number) {
    loading.value = true;
    error.value = null;
    try {
      const updated = await addPaperToProject(projectId, paperId);

      if (selectedProject.value?.project.project_id === projectId) {
        selectedProject.value = updated;
      }

      return updated;
    } catch (err) {
      error.value = 'Failed to add paper.';
      console.error(err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function removePaper(projectId: number, paperId: number) {
    loading.value = true;
    error.value = null;
    try {
      const updated = await removePaperFromProject(projectId, paperId);

      if (selectedProject.value?.project.project_id === projectId) {
        selectedProject.value = updated;
      }

      return updated;
    } catch (err) {
      error.value = 'Failed to remove paper.';
      console.error(err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    // state
    projects,
    selectedProject,
    loading,
    error,

    // actions
    loadProjects,
    selectProject,
    createNewProject,
    renameProject,
    deleteExistingProject,
    addPaper,
    removePaper,
  }
});
