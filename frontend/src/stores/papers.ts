import { fetchPaperPdf } from '@/services/papers'; // Check this path matches your file location

const pdfCache = new Map<number, Blob>();

export const PaperStore = {

    async getPdf(paperId: number): Promise<Blob> {
        if (pdfCache.has(paperId)) {
            return pdfCache.get(paperId)!;
        }

        const blob = await fetchPaperPdf(paperId);

        pdfCache.set(paperId, blob);
        return blob;
    },

    clearCache() {
        pdfCache.clear();
    }
};