<script setup lang="ts">
import { useRouter } from 'vue-router';
import SearchInputSection from '@/components/organisms/search/SearchInputSection.vue';
import { useSearchStore } from '@/stores/search';
import type { AdvancedSearchOptions } from '@/types/search';
import { serializeAdvancedOptions } from '@/composables/useAdvancedSearchUrl';

const router = useRouter();
const searchStore = useSearchStore();

const handleSearch = (payload: { query: string; file: File | null; advanced?: AdvancedSearchOptions } | string) => {
  const query = typeof payload === 'string' ? payload : payload.query;
  const file = typeof payload !== 'string' && payload.file ? payload.file : null;
  const advanced = typeof payload !== 'string' ? payload.advanced : undefined;

  if (file) {
    searchStore.setStagedFile(file);
  }

  const queryParams: Record<string, string> = { q: query };
  const serializedFilter = serializeAdvancedOptions(advanced);
  if (serializedFilter) {
    queryParams.filter = serializedFilter;
  }

  router.push({
    name: 'search',
    query: queryParams
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