<script setup lang="ts">
import { computed } from 'vue';
import MarkdownIt from 'markdown-it';
import markdownItKatex from 'markdown-it-katex';
import DOMPurify from 'dompurify';

const props = defineProps<{
  markdown: string;
}>();

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
});
md.use(markdownItKatex);

const rendered = computed(() => {
  const raw = md.render(props.markdown ?? "");
  return DOMPurify.sanitize(raw);
});
</script>

<template>
  <div class="md" v-html="rendered" />
</template>

<style scoped>
.md {
  line-height: 1.5;
  font-size: 0.95rem;
  color: rgba(0, 0, 0, 0.87);
}

/* Headings */
.md :deep(h1),
.md :deep(h2),
.md :deep(h3),
.md :deep(h4) {
  font-weight: 600;
  line-height: 1.35;
  margin: 10px 0 6px;
}

/* Paragraphs */
.md :deep(p) {
  margin: 0 0 6px;
}

/* Lists */
.md :deep(ul),
.md :deep(ol) {
  margin: 4px 0 6px;
  padding-left: 1.2rem;
}

.md :deep(li) {
  margin: 2px 0;
}

/* Avoid massive gaps between sections */
.md :deep(p + ul),
.md :deep(p + ol),
.md :deep(ul + p),
.md :deep(ol + p) {
  margin-top: 4px;
}

/* KaTeX math */
.md :deep(.katex-display) {
  margin: 6px 0;
}

/* Inline code */
.md :deep(code) {
  font-size: 0.9em;
}
</style>