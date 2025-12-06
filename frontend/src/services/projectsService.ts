import { computed } from 'vue';
import { useProjectsStore } from '@/stores/projects';

export function useProjectsService() {
  const projectsStore = useProjectsStore();

  const projects = computed(() => projectsStore.projects);
  const selectedProject = computed(() => projectsStore.selectedProject);
  const loading = computed(() => projectsStore.loading);
  const error = computed(() => projectsStore.error);

  const loadProjects = () => projectsStore.loadProjects();
  const selectProject = (projectId: number) => projectsStore.selectProject(projectId);
  const createProject = (name: string) => projectsStore.createNewProject(name);
  const renameProject = (projectId: number, newName: string) =>
    projectsStore.renameProject(projectId, newName);
  const deleteProject = (projectId: number) => projectsStore.deleteExistingProject(projectId);
  const addPaperToProject = (projectId: number, paperId: number) =>
    projectsStore.addPaper(projectId, paperId);
  const removePaperFromProject = (projectId: number, paperId: number) =>
    projectsStore.removePaper(projectId, paperId);
  const resetProjects = () => projectsStore.$reset();

  return {
    projects,
    selectedProject,
    loading,
    error,
    loadProjects,
    selectProject,
    createProject,
    renameProject,
    deleteProject,
    addPaperToProject,
    removePaperFromProject,
    resetProjects,
  };
}
