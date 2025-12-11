<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue';
import {
    VDialog, VCard, VCardTitle, VCardText, VBtn, VIcon,
    VSpacer, VProgressCircular, VAlert
} from 'vuetify/components';
import { X, Download } from 'lucide-vue-next';
import VuePdfEmbed from 'vue-pdf-embed';
import { fetchPaperPdf } from '@/services/papers';

const props = defineProps<{
    open: boolean;
    paperId: number | null;
    paperTitle?: string;
}>();

const emit = defineEmits<{
    (e: 'close'): void;
}>();

const loading = ref(false);
const error = ref<string | null>(null);
const pdfSource = ref<string | null>(null);

// -- Fetch Logic --
const loadPdf = async () => {
    if (!props.paperId) return;

    loading.value = true;
    error.value = null;

    // Clean up previous blob URL to avoid memory leaks
    if (pdfSource.value) {
        URL.revokeObjectURL(pdfSource.value);
        pdfSource.value = null;
    }

    try {
        const blob = await fetchPaperPdf(props.paperId);
        // Create a local URL for the binary data
        pdfSource.value = URL.createObjectURL(blob);
    } catch (err) {
        console.error('Failed to load PDF:', err);
        error.value = 'Failed to load the PDF document. Please try again later.';
    } finally {
        loading.value = false;
    }
};

// -- Watchers --
watch(() => props.open, (isOpen) => {
    if (isOpen && props.paperId) {
        loadPdf();
    }
});

// -- Cleanup --
onUnmounted(() => {
    if (pdfSource.value) {
        URL.revokeObjectURL(pdfSource.value);
    }
});

const handleDownload = () => {
    if (pdfSource.value && props.paperTitle) {
        const link = document.createElement('a');
        link.href = pdfSource.value;
        link.download = `${props.paperTitle.substring(0, 50)}.pdf`;
        link.click();
    }
};
</script>

<template>
<v-dialog
:model-value="open"
@update:model-value="val => !val && emit('close')"
fullscreen
transition="dialog-bottom-transition"
    >
    <v-card class="pdf-viewer-card">
<div class="pdf-toolbar d-flex align-center px-4 py-2 bg-grey-lighten-3 border-b">
<h3 class="text-subtitle-1 font-weight-medium text-truncate me-4" style="max-width: 600px;">
    {{ paperTitle || 'PDF Viewer' }}
</h3>
<v-spacer />

<v-btn
v-if="pdfSource"
    variant="text"
color="primary"
class="me-2"
@click="handleDownload"
    >
    <v-icon :icon="Download" start />
Download
</v-btn>

<v-btn icon variant="text" @click="emit('close')">
    <v-icon :icon="X" />
    </v-btn>
    </div>

    <v-card-text class="pdf-content pa-0 bg-grey-lighten-2 d-flex justify-center overflow-auto">

    <div v-if="loading" class="d-flex flex-column align-center mt-12">
    <v-progress-circular indeterminate color="primary" size="64" />
<p class="mt-4 text-medium-emphasis">Loading PDF...</p>
</div>

<div v-else-if="error" class="mt-12 w-100 px-4" style="max-width: 600px;">
    <v-alert type="error" variant="tonal" :text="error" />
    </div>

    <div v-else-if="pdfSource" class="pdf-wrapper py-8">
    <vue-pdf-embed :source="pdfSource" class="shadow-lg" />
    </div>

    </v-card-text>
    </v-card>
    </v-dialog>
    </template>

<style scoped>
.pdf-viewer-card {
    display: flex;
    flex-direction: column;
    height: 100vh;
}

.pdf-wrapper {
    width: 100%;
    max-width: 900px;
    min-height: 100%;
}

:deep(.vue-pdf-embed__page) {
    margin-bottom: 16px;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
}
</style>