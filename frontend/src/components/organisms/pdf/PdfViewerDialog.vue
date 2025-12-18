<script lang="ts" setup>
import { onUnmounted, ref, watch, nextTick } from 'vue';
import { VAlert, VBtn, VCard, VCardText, VDialog, VIcon, VProgressCircular, VSpacer, VDivider } from 'vuetify/components';
import { Download, X, ZoomIn, ZoomOut, ChevronLeft, ChevronRight, RotateCw } from 'lucide-vue-next';
import VuePdfEmbed from 'vue-pdf-embed';
import { usePaperStore } from '@/stores/papers';
import type { PDFDocumentProxy } from 'pdfjs-dist';

import 'vue-pdf-embed/dist/styles/textLayer.css';
import 'vue-pdf-embed/dist/styles/annotationLayer.css';

const SCROLL_ANIMATION_DURATION = 1000;

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

// Viewer State
const pdfWidth = ref(800);
const rotation = ref(0);
const pageCount = ref(0);
const userInputPage = ref(1);

// Flag to prevent flickering during auto-scroll
const isAutoScrolling = ref(false);

const paperStore = usePaperStore();
let observer: IntersectionObserver | null = null;

const loadPdf = async () => {
  if (!props.paperId) return;

  loading.value = true;
  error.value = null;
  pdfWidth.value = 800;
  rotation.value = 0;
  userInputPage.value = 1;
  isAutoScrolling.value = false;

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

// --- Page Navigation Logic ---

const setupPageObserver = () => {
  if (observer) observer.disconnect();

  observer = new IntersectionObserver((entries) => {
    if (isAutoScrolling.value) return;

    // Find the page with the highest visibility ratio
    const visiblePage = entries.reduce((max, entry) => {
      return entry.intersectionRatio > max.intersectionRatio ? entry : max;
    }, entries[0]);

    if (visiblePage && visiblePage.intersectionRatio > 0.1) {
      const allPages = Array.from(document.querySelectorAll('.vue-pdf-embed > div'));
      const index = allPages.indexOf(visiblePage.target as Element);

      if (index !== -1) {
        const pageNum = index + 1;
        // Only update input if user isn't currently typing
        if (document.activeElement?.id !== 'page-input-field') {
          userInputPage.value = pageNum;
        }
      }
    }
  }, {
    root: document.querySelector('.pdf-scroll-container'),
    threshold: [0.1, 0.5]
  });

  const pages = document.querySelectorAll('.vue-pdf-embed > div');
  pages.forEach((page) => observer?.observe(page));
};

const handleDocumentLoaded = (doc: PDFDocumentProxy) => {
  pageCount.value = doc.numPages;
  loading.value = false;
  nextTick(() => setupPageObserver());
};

const scrollToPage = (pageNumber: number) => {
  if (pageNumber < 1 || pageNumber > pageCount.value) return;

  const pages = document.querySelectorAll('.vue-pdf-embed > div');
  const targetPage = pages[pageNumber - 1];

  if (targetPage) {
    isAutoScrolling.value = true;

    // Explicitly set the number to the target immediately (e.g. "8")
    userInputPage.value = pageNumber;

    targetPage.scrollIntoView({ behavior: 'smooth', block: 'start' });

    setTimeout(() => {
      isAutoScrolling.value = false;
    }, SCROLL_ANIMATION_DURATION);
  }
};

const jumpToPage = () => {
  let p = typeof userInputPage.value === 'string' ? parseInt(userInputPage.value) : userInputPage.value;
  if (isNaN(p) || p < 1) p = 1;
  if (p > pageCount.value) p = pageCount.value;
  scrollToPage(p);
};

const nextPage = () => {
  const current = typeof userInputPage.value === 'string' ? parseInt(userInputPage.value) : userInputPage.value;
  if (current < pageCount.value) scrollToPage(current + 1);
};

const prevPage = () => {
  const current = typeof userInputPage.value === 'string' ? parseInt(userInputPage.value) : userInputPage.value;
  if (current > 1) scrollToPage(current - 1);
};

const handleInputFocus = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target) {
    target.select();
  }
};

// --- View Controls ---

const zoomIn = () => { if (pdfWidth.value < 2500) pdfWidth.value += 150; };
const zoomOut = () => { if (pdfWidth.value > 400) pdfWidth.value -= 150; };

const rotateDoc = () => {
  rotation.value = (rotation.value + 90) % 360;
};

const handleLinkClick = (pageNumber: number) => scrollToPage(pageNumber);

const handleDownload = () => {
  if (pdfSource.value && props.paperTitle) {
    const link = document.createElement('a');
    link.href = pdfSource.value;
    const safeName = props.paperTitle.replace(/[/\\?%*:|"<>]/g, '-');
    link.download = `${safeName}.pdf`;
    link.click();
  }
};

watch(() => props.open, (isOpen) => {
  if (isOpen && props.paperId) loadPdf();
  else if (!isOpen) {
    if (pdfSource.value) {
      URL.revokeObjectURL(pdfSource.value);
      pdfSource.value = null;
    }
    if (observer) observer.disconnect();
  }
});

onUnmounted(() => {
  if (pdfSource.value) URL.revokeObjectURL(pdfSource.value);
  if (observer) observer.disconnect();
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
      <div class="pdf-toolbar d-flex align-center px-4 py-2 bg-surface border-b">
        <h3 class="text-subtitle-1 font-weight-medium me-4 text-truncate" style="max-width: 300px;">
          {{ paperTitle || 'PDF Viewer' }}
        </h3>

        <v-spacer />

        <div
            class="d-flex align-center bg-background rounded px-2 py-1 border"
        >

          <v-btn icon size="x-small" variant="text" @click="prevPage" :disabled="userInputPage <= 1">
            <v-icon :icon="ChevronLeft" size="20" />
          </v-btn>

          <div class="d-flex align-center mx-1">
            <input
                id="page-input-field"
                v-model="userInputPage"
                type="number"
                class="page-input text-body-2 font-weight-bold"
                :max="pageCount"
                min="1"
                @keydown.enter="jumpToPage"
                @focus="$event.target.select()"
            />
            <span class="text-caption text-medium-emphasis ms-1">
               / {{ pageCount }}
            </span>
          </div>

          <v-btn icon size="x-small" variant="text" @click="nextPage" :disabled="userInputPage >= pageCount">
            <v-icon :icon="ChevronRight" size="20" />
          </v-btn>

          <v-divider vertical class="mx-2" style="height: 20px" />

          <v-btn icon size="x-small" variant="text" @click="zoomOut" density="comfortable">
            <v-icon :icon="ZoomOut" size="18" />
          </v-btn>

          <span class="text-caption font-weight-bold mx-1" style="min-width: 40px; text-align: center">
            {{ Math.round((pdfWidth / 800) * 100) }}%
          </span>

          <v-btn icon size="x-small" variant="text" @click="zoomIn" density="comfortable">
            <v-icon :icon="ZoomIn" size="18" />
          </v-btn>

          <v-divider vertical class="mx-2" style="height: 20px" />

          <v-btn icon size="x-small" variant="text" @click="rotateDoc" density="comfortable">
            <v-icon :icon="RotateCw" size="18" />
            <v-tooltip activator="parent" location="bottom">Rotate</v-tooltip>
          </v-btn>

        </div>

        <v-spacer />

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
          <v-alert :text="error" style="max-width: 600px" type="error" variant="tonal" />
        </div>

        <div v-if="pdfSource" class="pdf-scroll-container">
          <vue-pdf-embed
              :annotation-layer="true"
              :source="pdfSource"
              :text-layer="true"
              :width="pdfWidth"
              :rotation="rotation"
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
  transition: transform 0.2s ease; /* Smooth rotation */
}

/* Page Input Styling */
.page-input {
  width: 36px;
  text-align: right;
  border: none;
  background: transparent;
  outline: none;
  color: rgb(var(--v-theme-on-surface));
  -moz-appearance: textfield;
}
.page-input::-webkit-outer-spin-button,
.page-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.page-input:focus {
  border-bottom: 2px solid rgb(var(--v-theme-primary));
}

:deep(.vue-pdf-embed > div) {
  position: relative !important;
  margin-bottom: 24px;
  background-color: white;
}

:deep(.textLayer) {
  z-index: 1 !important;
  opacity: 1;
  mix-blend-mode: multiply;
  line-height: 1;
}

:deep(.annotationLayer) {
  z-index: 10 !important;
}

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