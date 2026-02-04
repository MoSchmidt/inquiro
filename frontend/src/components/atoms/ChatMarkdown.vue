<script setup lang="ts">
import { computed } from 'vue';
import MarkdownIt from 'markdown-it';
import markdownItKatex from 'markdown-it-katex';
import DOMPurify from 'dompurify';

const props = defineProps<{
  content: string;
}>();

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true, // Converts \n to <br>
});
md.use(markdownItKatex);

const rendered = computed(() => {
  const raw = md.render(props.content || '');
  return DOMPurify.sanitize(raw);
});
</script>

<template>
  <div class="chat-markdown text-body-2" v-html="rendered" />
</template>

<style scoped>
/* General Paragraphs */
.chat-markdown :deep(p) {
  margin-bottom: 8px;
}

/* Remove margin from the very last element to fit the chat bubble perfectly */
.chat-markdown :deep(*:last-child) {
  margin-bottom: 0 !important;
}

/* Lists */
.chat-markdown :deep(ul),
.chat-markdown :deep(ol) {
  margin-bottom: 8px;
  padding-left: 20px;
  list-style-type: disc;
}

.chat-markdown :deep(ol) {
  list-style-type: decimal;
}

/* Code Blocks */
.chat-markdown :deep(pre) {
  background-color: rgb(var(--v-theme-surface-variant), 0.3);
  border-radius: 6px;
  padding: 8px;
  margin: 8px 0;
  overflow-x: auto;
  font-family: monospace;
}

/* Inline Code */
.chat-markdown :deep(code) {
  background-color: rgb(var(--v-theme-surface-variant), 0.3);
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
}
</style>