<script setup lang="ts">
import { useRouter } from 'vue-router';
import SearchInputSection from '@/components/organisms/search/SearchInputSection.vue';

const router = useRouter();

const handleSearch = (payload: { query: string; file: File | null } | string) => {
  const query = typeof payload === 'string' ? payload : payload.query;
  const file = typeof payload !== 'string' && payload.file ? payload.file : null;

  // Navigate to the search route.
  // We pass strings via query params, and Files via history state
  router.push({
    name: 'search',
    query: { q: query },
    state: { file: file } // Pass the file object invisibly via History API
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
  /* Center vertically like the original start screen often does */
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>