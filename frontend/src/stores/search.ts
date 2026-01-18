import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { AdvancedSearchOptions } from '@/types/search';

export const useSearchStore = defineStore('search', () => {
    const stagedFile = ref<File | null>(null);
    const stagedAdvancedOptions = ref<AdvancedSearchOptions | null>(null);

    const setStagedFile = (file: File | null) => {
        stagedFile.value = file;
    };

    const setStagedAdvancedOptions = (options: AdvancedSearchOptions | null) => {
        stagedAdvancedOptions.value = options;
    };

    return {
        stagedFile,
        setStagedFile,
        stagedAdvancedOptions,
        setStagedAdvancedOptions,
    };
});