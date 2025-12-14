import { fetchPaperPdf } from '@/services/papers'; // Check this path matches your file location

// A simple Map to hold cached blobs: ID -> Blob
const pdfCache = new Map<number, Blob>();

export const PaperStore = {
    /**
     * Gets a PDF. Returns cached version if available, otherwise fetches it.
     */
    async getPdf(paperId: number): Promise<Blob> {
        // 1. Check Cache
        if (pdfCache.has(paperId)) {
            console.log(`[Store] Returning cached PDF for ${paperId}`);
            return pdfCache.get(paperId)!;
        }

        // 2. Fetch from API (using your new service)
        console.log(`[Store] Fetching fresh PDF for ${paperId}`);
        const blob = await fetchPaperPdf(paperId);

        // 3. Save to Cache
        pdfCache.set(paperId, blob);
        return blob;
    },

    // Optional helper to clear cache (e.g. on logout)
    clearCache() {
        pdfCache.clear();
    }
};