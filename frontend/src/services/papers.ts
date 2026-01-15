import { PaperApi, PaperSummaryRequest, PaperSummaryResponse } from '@/api';
import { apiAxios } from '@/auth/axios-auth';

const paperApi = new PaperApi(undefined, undefined, apiAxios);

export async function fetchPaperPdf(paperId: number): Promise<Blob> {
    const response = await paperApi.getPaperPdfPapersPaperIdPdfGet(paperId, {
        responseType: 'blob'
    });

    return response.data as unknown as Blob;
}

export async function summarisePaper(paperId: number, query: string = ""): Promise<PaperSummaryResponse> {
    const request: PaperSummaryRequest = {
        query: query,
    };
    const response = await paperApi.summaryPapersPaperIdSummaryPost(paperId, request);
    return response.data;
}
