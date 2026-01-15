import type { Paper } from '@/types/content';
import { PaperDto, ProjectWithPapersResponse, SearchResponse } from '@/api';

export function mapProjectWithPapersResponseToPapers(project: ProjectWithPapersResponse): Paper[] {
  return project.papers.map(p => (mapPaperDtoToPaper(p)));
}

export function mapSearchResponseToPapers(searchResponse: SearchResponse): Paper[] {
  return searchResponse.papers.map(p => mapPaperDtoToPaper(p));
}

export function mapPaperDtoToPaper(paperDto: PaperDto): Paper {
    return {
      paper_id: paperDto.paper_id,
      title: paperDto.title,
      author: paperDto.authors ? Object.values(paperDto.authors).join(', ') : '',
      year: paperDto.published_at ? new Date(paperDto.published_at).getFullYear() : 0,
      abstract: paperDto.abstract ?? undefined,
    };
}
