import { ProjectCreate, ProjectsApi, ProjectUpdate } from '@/api';
import { apiAxios } from '@/auth/axios-auth';

const projectApi = new ProjectsApi(undefined, undefined, apiAxios);

export async function listProjects() {
  const response = await projectApi.listProjectsProjectsGet();
  return response.data;
}

export async function createProject(payload: ProjectCreate) {
  const response = await projectApi.createProjectProjectsPost(payload);
  return response.data;
}

export async function getProject(projectId: number) {
  const response = await projectApi.getPapersForProjectProjectsProjectIdPapersGet(projectId);
  return response.data;
}

export async function updateProject(projectId: number, payload: ProjectUpdate) {
  const response = await projectApi.updateProjectProjectsProjectIdPatch(projectId, payload);
  return response.data;
}

export async function deleteProject(projectId: number) {
  await projectApi.deleteProjectProjectsProjectIdDelete(projectId);
}

export async function addPaperToProject(projectId: number, paperId: number) {
  const response = await projectApi.addPaperToProjectProjectsProjectIdPapersPaperIdPost(projectId, paperId);
  return response.data;
}

export async function removePaperFromProject(projectId: number, paperId: number) {
  const response = await projectApi.removePaperFromProjectProjectsProjectIdPapersPaperIdDelete(projectId, paperId);
  return response.data;
}


