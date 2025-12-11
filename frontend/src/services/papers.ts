import { apiAxios } from '@/auth/axios-auth';
// 1. Import the BASE_PATH configuration
import { BASE_PATH } from '@/api/base';

/**
 * Fetches the PDF binary for a specific paper.
 * Returns a Blob that can be displayed in a viewer.
 */
export async function fetchPaperPdf(paperId: number): Promise<Blob> {
    // 2. Prepend BASE_PATH to the URL
    const response = await apiAxios.get(`${BASE_PATH}/papers/${paperId}/pdf`, {
        responseType: 'blob',
        headers: {
            'Accept': 'application/pdf',
        },
    });
    return response.data;
}