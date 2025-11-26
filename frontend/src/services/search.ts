import api from '../api/axios';

export interface SearchPaper {
  paper_id: number;
  title: string;
  authors?: Record<string, string> | null;
  abstract?: string | null;
  published_at?: string | null;
  url?: string | null;
}

export interface SearchResponse {
  papers: SearchPaper[];
}

export async function searchPapers(query: string): Promise<SearchResponse> {
  const response = await api.post<SearchResponse>('/search', { query });
  return response.data;
}

