<script lang="ts" setup>
import { onUnmounted, ref, watch } from 'vue';
import { VAlert, VBtn, VCard, VCardText, VDialog, VIcon, VProgressCircular, VSpacer, } from 'vuetify/components';
import { Download, X, ZoomIn, ZoomOut } from 'lucide-vue-next';
import VuePdfEmbed from 'vue-pdf-embed';
import { usePaperStore } from '@/stores/papers';
import type { PDFDocumentProxy } from 'pdfjs-dist';

import 'vue-pdf-embed/dist/styles/textLayer.css';
import 'vue-pdf-embed/dist/styles/annotationLayer.css';

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

const pdfWidth = ref(800);
const pageCount = ref(0);

const paperStore = usePaperStore();

const loadPdf = async () => {
  if (!props.paperId) return;

  loading.value = true;
  error.value = null;
  pdfWidth.value = 800;

  if (pdfSource.value) {
    URL.revokeObjectURL(pdfSource.value);
    pdfSource.value = null;
  }

  try {
    const blob = await paperStore.getPdf(props.paperId);
    pdfSource.value = URL.createObjectURL(blob);
  } catch (err) {
    console.error('Failed to load PDF:', err);
    error.value = 'Failed to load the PDF document. Please try again later.';
    loading.value = false;
  }
};

const handleDocumentLoaded = (doc: PDFDocumentProxy) => {
  pageCount.value = doc.numPages;
  loading.value = false;
};

//Handle Internal Links
const handleLinkClick = (pageNumber: number) => {
  if (pageNumber) {
    const pageElement = document.querySelector(
        `.pdf-document .page[data-page-number="${pageNumber}"]`
    );

    if (pageElement) {
      pageElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
};

const zoomIn = () => {
  if (pdfWidth.value < 2000) pdfWidth.value += 150;
};

const zoomOut = () => {
  if (pdfWidth.value > 400) pdfWidth.value -= 150;
};

const handleDownload = () => {
  if (pdfSource.value && props.paperTitle) {
    const link = document.createElement('a');
    link.href = pdfSource.value;
    const safeName = props.paperTitle.replace(/[/\\?%*:|"<>]/g, '-');
    link.download = `${safeName}.pdf`;
    link.click();
  }
};

watch(
    () => props.open,
    (isOpen) => {
      if (isOpen && props.paperId) {
        loadPdf();
      } else if (!isOpen && pdfSource.value) {
        URL.revokeObjectURL(pdfSource.value);
        pdfSource.value = null;
      }
    }
);

onUnmounted(() => {
  if (pdfSource.value) {
    URL.revokeObjectURL(pdfSource.value);
  }
});
</script>

<template>
  <v-dialog
      :model-value="open"
      class="pdf-dialog"
      fullscreen
      transition="dialog-bottom-transition"
      @update:model-value="(val) => !val && emit('close')"
  >
    <v-card class="pdf-viewer-card">
      <div
          class="pdf-toolbar d-flex align-center px-4 py-2 bg-surface border-b"
      >
        <h3 class="text-subtitle-1 font-weight-medium me-4">
          {{ paperTitle || 'PDF Viewer' }}
        </h3>

        <v-spacer />

        <div class="d-flex align-center me-4">
          <span class="text-caption font-weight-bold mx-2 text-medium-emphasis">
            {{ pageCount > 0 ? `${pageCount} Pages` : '' }}
          </span>
          <v-divider class="mx-2" vertical />

          <v-btn icon size="small" variant="text" @click="zoomOut">
            <v-icon :icon="ZoomOut" size="20" />
          </v-btn>

          <span
              class="text-caption font-weight-bold mx-2"
              style="min-width: 40px; text-align: center"
          >
            {{ Math.round((pdfWidth / 800) * 100) }}%
          </span>

          <v-btn icon size="small" variant="text" @click="zoomIn">
            <v-icon :icon="ZoomIn" size="20" />
          </v-btn>
        </div>

        <v-btn
            v-if="pdfSource"
            class="me-2 text-none"
            color="primary"
            size="small"
            variant="flat"
            @click="handleDownload"
        >
          <v-icon :icon="Download" size="18" start />
          Download
        </v-btn>

        <v-btn icon variant="text" @click="emit('close')">
          <v-icon :icon="X" />
        </v-btn>
      </div>

      <v-card-text class="pdf-content pa-0 bg-background position-relative">

        <div
            v-if="loading"
            class="d-flex flex-column align-center justify-center position-absolute w-100 h-100 bg-surface"
            style="z-index: 10; opacity: 0.9"
        >
          <v-progress-circular color="primary" indeterminate size="64" />
          <p class="mt-4 text-medium-emphasis">Loading PDF...</p>
        </div>

        <div v-if="error" class="d-flex justify-center mt-12 w-100 px-4">
          <v-alert
              :text="error"
              style="max-width: 600px"
              type="error"
              variant="tonal"
          />
        </div>

        <div v-if="pdfSource" class="pdf-scroll-container">
          <vue-pdf-embed
              :annotation-layer="true"
              :source="pdfSource"
              :text-layer="true"
              :width="pdfWidth"
              class="pdf-document"
              @loaded="handleDocumentLoaded"
              @internal-link-clicked="handleLinkClick"
          />
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
  overflow: hidden;
}

.pdf-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.pdf-scroll-container {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  overflow-x: auto;
  display: flex;
  justify-content: center;
  padding: 32px 0;
}

.pdf-document {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* This keeps the actual PDF pages WHITE even in Dark Mode (Standard behavior) */
:deep(.vue-pdf-embed > div) {
  position: relative !important;
  margin-bottom: 24px;
  background-color: white;
}

/* 1. Text Layer: MUST be below annotations */
:deep(.textLayer) {
  z-index: 1 !important;
  opacity: 1;
  mix-blend-mode: multiply;
  line-height: 1;
}

/* 2. Annotation Layer: MUST be above text */
:deep(.annotationLayer) {
  z-index: 10 !important;
}

/* 3. Make links strictly clickable */
:deep(.annotationLayer section),
:deep(.annotationLayer a) {
  cursor: pointer !important;
  pointer-events: auto !important;
}

:deep(.annotationLayer a:hover) {
  background-color: rgba(255, 255, 0, 0.2);
  outline: 2px solid rgba(255, 255, 0, 0.5);
}

:deep(.textLayer span) {
  color: transparent;
  cursor: text;
}

:deep(::selection) {
  background: rgba(0, 0, 255, 0.2);
}
</style>