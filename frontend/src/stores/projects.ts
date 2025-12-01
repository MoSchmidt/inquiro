import { defineStore } from 'pinia';
import {
  addPaperToProject,
  createProject,
  deleteProject,
  getProject,
  listProjects,
  removePaperFromProject,
  updateProject,
} from '@/services/projects';
import { ProjectResponse, ProjectWithPapersResponse } from '@/api';

interface ProjectsState {
  projects: ProjectResponse[];
  selectedProject: ProjectWithPapersResponse | null;
  loading: boolean;
  error: string | null;
}

export const useProjectsStore = defineStore('projects', {
  state: (): ProjectsState => ({
    projects: [],
    selectedProject: null,
    loading: false,
    error: null,
  }),

  actions: {
    async loadProjects() {
      this.loading = true;
      this.error = null;
      try {
        this.projects = await listProjects();
      } catch (error) {
        this.error = 'Failed to load projects.';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },

    async selectProject(projectId: number) {
      this.loading = true;
      this.error = null;
      try {
        this.selectedProject = await getProject(projectId);
      } catch (error) {
        this.error = 'Failed to load project.';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },

    async createNewProject(name: string) {
      this.loading = true;
      this.error = null;
      try {
        const project = await createProject({ project_name: name });
        this.projects.unshift(project);
        return project;
      } catch (error) {
        this.error = 'Failed to create project.';
        console.error(error);
        return null;
      } finally {
        this.loading = false;
      }
    },

    async renameProject(projectId: number, newName: string) {
      this.loading = true;
      this.error = null;
      try {
        const updated = await updateProject(projectId, { project_name: newName });
        this.projects = this.projects.map((p) =>
          p.project_id === projectId ? updated : p,
        );
        if (this.selectedProject && this.selectedProject.project.project_id === projectId) {
          this.selectedProject = {
            ...this.selectedProject,
            project: updated,
          };
        }
      } catch (error) {
        this.error = 'Failed to update project.';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },

    async deleteExistingProject(projectId: number) {
      this.loading = true;
      this.error = null;
      try {
        await deleteProject(projectId);
        this.projects = this.projects.filter((p) => p.project_id !== projectId);
        if (this.selectedProject && this.selectedProject.project.project_id === projectId) {
          this.selectedProject = null;
        }
      } catch (error) {
        this.error = 'Failed to delete project.';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },

    async addPaper(projectId: number, paperId: number) {
      this.loading = true;
      this.error = null;
      try {
        const projectWithPapers = await addPaperToProject(projectId, paperId);
        if (this.selectedProject && this.selectedProject.project.project_id === projectId) {
          this.selectedProject = projectWithPapers;
        }
      } catch (error) {
        this.error = 'Failed to add paper to project.';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },

    async removePaper(projectId: number, paperId: number) {
      this.loading = true;
      this.error = null;
      try {
        const projectWithPapers = await removePaperFromProject(projectId, paperId);
        if (this.selectedProject && this.selectedProject.project.project_id === projectId) {
          this.selectedProject = projectWithPapers;
        }
      } catch (error) {
        this.error = 'Failed to remove paper from project.';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
  },
});


