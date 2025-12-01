import { SearchApi, SearchRequest, SearchResponse } from '@/api';
import { apiAxios } from '@/auth/axios-auth';

const searchApi = new SearchApi(undefined, undefined, apiAxios);

export async function searchPapers(searchText: string): Promise<SearchResponse> {
  const request: SearchRequest = {
    query: searchText,
  };
  const response = await searchApi.searchSearchPost(request);
  return response.data;
}
