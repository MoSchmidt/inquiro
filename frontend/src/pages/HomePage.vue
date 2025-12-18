<script setup lang="ts">
import { useRouter } from 'vue-router';
import SearchInputSection from '@/components/organisms/search/SearchInputSection.vue';
import { useSearchStore } from '@/stores/search';

const router = useRouter();
const searchStore = useSearchStore();

const handleSearch = (payload: { query: string; file: File | null } | string) => {
  const query = typeof payload === 'string' ? payload : payload.query;
  const file = typeof payload !== 'string' && payload.file ? payload.file : null;

  // 1. Store the file in Pinia
  if (file) {
    searchStore.setStagedFile(file);
  }

  // 2. Navigate
  router.push({
    name: 'search',
    query: { q: query }
  });
};
</script>

<template>
  <div class="home-page">
    <SearchInputSection @submit="handleSearch" />
  </div>
</template>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 8px;
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>