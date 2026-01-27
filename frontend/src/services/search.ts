import { SearchApi, type AdvancedSearchFilter, type SearchRequest, type SearchResponse } from '@/api';
import { apiAxios } from '@/auth/axios-auth';
import type { AdvancedSearchOptions } from '@/types/search';

const searchApi = new SearchApi(undefined, undefined, apiAxios);

function toFilterDto(advanced?: AdvancedSearchOptions): AdvancedSearchFilter | undefined {
  if (!advanced) return undefined;
  return {
    year_from: advanced.yearFrom ?? null,
    year_to: advanced.yearTo ?? null,
    root: advanced.root as AdvancedSearchFilter['root'],
  };
}

export async function searchPapers(searchText: string, advanced?: AdvancedSearchOptions): Promise<SearchResponse> {
  const request: SearchRequest = {
    query: searchText,
    filter: toFilterDto(advanced),
  };
  const response = await searchApi.searchSearchPost(request);
  return response.data;
}

export async function searchPapersByPdf(file: File, query?: string, advanced?: AdvancedSearchOptions): Promise<SearchResponse> {
  const filterJson = advanced ? JSON.stringify(toFilterDto(advanced)) : undefined;
  const response = await searchApi.searchByPdfSearchPdfPost(file, query, filterJson);
  return response.data;
}
