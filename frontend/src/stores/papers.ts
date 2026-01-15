import { defineStore } from 'pinia';
import { fetchPaperPdf } from '@/services/papers';

const MAX_PDF_CACHE_SIZE = 40;

export const usePaperStore = defineStore('paper', () => {
    // module-scoped cache (shared across all store instances)
    const pdfCache = new Map<number, Blob>();

    async function getPdf(paperId: number): Promise<Blob> {
        const cached = pdfCache.get(paperId);
        if (cached) {
            // refresh LRU position by reinserting the cached entry
            pdfCache.delete(paperId);
            pdfCache.set(paperId, cached);
            return cached;
        }

        // enforce a max cache size using a simple LRU eviction strategy
        if (pdfCache.size >= MAX_PDF_CACHE_SIZE) {
            const oldestKey = pdfCache.keys().next().value as number | undefined;
            if (oldestKey !== undefined) {
                pdfCache.delete(oldestKey);
            }
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
