import api from '../api/axios';

export interface PaperSummary {
  paper_id: number;
  title: string;
  authors?: Record<string, string> | null;
  abstract?: string | null;
  published_at?: string | null;
  url?: string | null;
  pdf_url?: string | null;
}

export interface Project {
  project_id: number;
  project_name: string;
  created_at: string;
}

export interface ProjectWithPapers {
  project: Project;
  papers: PaperSummary[];
}

export interface ProjectCreatePayload {
  project_name: string;
}

export interface ProjectUpdatePayload {
  project_name?: string;
}

export async function listProjects() {
  const response = await api.get<Project[]>('/projects');
  return response.data;
}

export async function createProject(payload: ProjectCreatePayload) {
  const response = await api.post<Project>('/projects', payload);
  return response.data;
}

export async function getProject(projectId: number) {
  const response = await api.get<ProjectWithPapers>(`/projects/${projectId}`);
  return response.data;
}

export async function updateProject(projectId: number, payload: ProjectUpdatePayload) {
  const response = await api.patch<Project>(`/projects/${projectId}`, payload);
  return response.data;
}

export async function deleteProject(projectId: number) {
  await api.delete(`/projects/${projectId}`);
}

export async function addPaperToProject(projectId: number, paperId: number) {
  const response = await api.post<ProjectWithPapers>(
    `/projects/${projectId}/papers`,
    null,
    { params: { paper_id: paperId } },
  );
  return response.data;
}

export async function removePaperFromProject(projectId: number, paperId: number) {
  const response = await api.delete<ProjectWithPapers>(
    `/projects/${projectId}/papers/${paperId}`,
  );
  return response.data;
}


