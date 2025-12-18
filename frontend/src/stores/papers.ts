import { defineStore } from 'pinia';
import { fetchPaperPdf } from '@/services/papers';

export const usePaperStore = defineStore('paper', () => {
    // module-scoped cache (shared across all store instances)
    const pdfCache = new Map<number, Blob>();

    async function getPdf(paperId: number): Promise<Blob> {
        const cached = pdfCache.get(paperId);
        if (cached) return cached;

        if (pdfCache.size > 40) {
            pdfCache.clear();
        }

        const blob = await fetchPaperPdf(paperId);
        pdfCache.set(paperId, blob);
        return blob;
    }

    function clearCache() {
        pdfCache.clear();
    }

    return {
        getPdf,
        clearCache,
    };
});
