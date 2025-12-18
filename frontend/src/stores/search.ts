import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useSearchStore = defineStore('search', () => {
    const stagedFile = ref<File | null>(null);

    const setStagedFile = (file: File | null) => {
        stagedFile.value = file;
    };

    return {
        stagedFile,
        setStagedFile,
    };
});