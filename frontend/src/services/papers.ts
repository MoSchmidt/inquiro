import { PaperApi } from '@/api';
import { apiAxios } from '@/auth/axios-auth';

const paperApi = new PaperApi(undefined, undefined, apiAxios);

export async function fetchPaperPdf(paperId: number): Promise<Blob> {
    const response = await paperApi.getPaperPdfPapersPaperIdPdfGet(paperId, {
        responseType: 'blob'
    });

    return response.data as unknown as Blob;
}
