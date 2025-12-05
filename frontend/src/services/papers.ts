import type {
  PaperResponse,
  ProjectResponse,
  ProjectWithPapersResponse,
  SearchResponse,
} from '@/api';
import type { Paper, Project } from '@/types/content';
import { searchPapers } from './search';

function mapAuthors(authors?: Record<string, string> | null): string {
  return authors ? Object.values(authors).join(', ') : '';
}

function mapPublishedYear(date?: string | null): number {
  return date ? new Date(date).getFullYear() : 0;
}

export function toPaper(paper: PaperResponse): Paper {
  return {
    paper_id: paper.paper_id,
    title: paper.title,
    author: mapAuthors(paper.authors),
    year: mapPublishedYear(paper.published_at),
    abstract: paper.abstract ?? undefined,
  };
}

export function toSidebarProjects(projects: ProjectResponse[]): Project[] {
  return projects.map((project) => ({
    id: project.project_id,
    name: project.project_name,
    date: project.created_at.split('T')[0],
    outputs: [],
  }));
}

export async function performSearch(query: string): Promise<SearchResponse> {
  return searchPapers(query);
}

export function mapSearchResultToPapers(response: SearchResponse): Paper[] {
  return response.papers.map(toPaper);
}

export function mapProjectPapers(project: ProjectWithPapersResponse | null): Paper[] {
  if (!project) return [];
  return project.papers.map(toPaper);
}
