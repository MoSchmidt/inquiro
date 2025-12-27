<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import type { AdvancedSearchOptions, ConditionGroup } from '@/types/search';
import AdvancedSearchGroup from '@/components/molecules/AdvancedSearchGroup.vue';
import { ChevronDown, X } from 'lucide-vue-next';
import ExpansionChevron from '@/components/atoms/ExpansionChevron.vue';

const emit = defineEmits<{
  (e: 'update', value: AdvancedSearchOptions): void;
}>();

const currentYear = new Date().getFullYear();
const years = computed(() =>
  Array.from({ length: 100 }, (_, i) => currentYear - i)
);

const yearFrom = ref<number | undefined>();
const yearTo = ref<number | undefined>();

const root = ref<ConditionGroup>({
  type: 'group',
  operator: 'AND',
  children: [],
});

const hasActiveFilters = computed(() => {
  return (
    yearFrom.value !== undefined ||
    yearTo.value !== undefined ||
    root.value.children.length > 0
  );
});

const clearAll = () => {
  yearFrom.value = undefined;
  yearTo.value = undefined;

  root.value = {
    type: 'group',
    operator: 'AND',
    children: [],
  };
};

watch(
  [yearFrom, yearTo, root],
  () => {
    emit('update', {
      yearFrom: yearFrom.value ?? undefined,
      yearTo: yearTo.value ?? undefined,
      root: root.value,
    });
  },
  { deep: true }
);
</script>

<template>
  <v-expansion-panels flat rounded="lg">
    <v-expansion-panel>
      <v-expansion-panel-title v-slot="{ expanded }">
        <div class="d-flex align-center justify-space-between w-100">
          <div class="d-flex align-center ga-2">
            <ExpansionChevron :expanded="expanded" />
            <span>Advanced search</span>
          </div>
          <v-btn
            variant="text"
            class="text-caption"
            :disabled="!hasActiveFilters"
            @click.stop="clearAll"
          >
            Clear all
          </v-btn>
        </div>
      </v-expansion-panel-title>

      <v-expansion-panel-text>
        <!-- Year filters -->
        <v-row>
          <v-col cols="6">
            <v-autocomplete
              v-model="yearFrom"
              :items="years"
              variant="outlined"
              label="Published from"
              clearable
              :clear-icon="X"
              :menu-icon="ChevronDown"
              density="compact"
              hide-details
            />
          </v-col>

          <v-col cols="6">
            <v-autocomplete
              v-model="yearTo"
              :items="years"
              variant="outlined"
              label="Published to"
              clearable
              :clear-icon="X"
              :menu-icon="ChevronDown"
              density="compact"
              hide-details
            />
          </v-col>
        </v-row>

        <AdvancedSearchGroup v-model="root" class="mt-5" :is-root="true" />
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>