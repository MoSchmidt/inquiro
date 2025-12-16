<script setup lang="ts">
import { computed, watchEffect } from 'vue';
import { VBtn, VIcon, VSelect, VTextField, VTooltip } from 'vuetify/components';
import { ChevronDown, X } from 'lucide-vue-next';
import type { TextCondition } from '@/types/search';

const model = defineModel<TextCondition>({ required: true });

const fieldItems = [
  { title: 'Title', value: 'title' },
  { title: 'Abstract', value: 'abstract' },
] as const satisfies ReadonlyArray<{
  title: string;
  value: TextCondition['field'];
}>;

const operatorItems = [
  { title: 'Contains', value: 'contains' },
  { title: 'Does not contain', value: 'not_contains' },
] as const satisfies ReadonlyArray<{
  title: string;
  value: TextCondition['operator'];
}>;

watchEffect(() => {
  const next: TextCondition = {
    ...model.value,
    field: model.value.field ?? fieldItems[0].value,
    operator: model.value.operator ?? operatorItems[0].value,
    value: model.value.value ?? '',
  };

  // avoid emitting if nothing changed
  if (
    next.field !== model.value.field ||
    next.operator !== model.value.operator ||
    next.value !== model.value.value
  ) {
    model.value = next;
  }
});

// Computed proxies per field (official pattern for nested v-model)
const field = computed<TextCondition['field']>({
  get: () => model.value.field,
  set: (v) => (model.value = { ...model.value, field: v }),
});

const operator = computed<TextCondition['operator']>({
  get: () => model.value.operator,
  set: (v) => (model.value = { ...model.value, operator: v }),
});

const text = computed<TextCondition['value']>({
  get: () => model.value.value,
  set: (v) => (model.value = { ...model.value, value: v }),
});

const remove = defineEmits<{ (e: 'remove'): void }>();
</script>

<template>
  <div class="d-flex align-center" style="gap: 12px">
    <v-select
      v-model="field"
      :items="fieldItems"
      item-title="title"
      item-value="value"
      variant="outlined"
      density="compact"
      hide-details
      :menu-icon="ChevronDown"
      style="max-width: 180px"
      :menu-props="{ closeOnContentClick: true }"
    />

    <v-select
      v-model="operator"
      :items="operatorItems"
      item-title="title"
      item-value="value"
      variant="outlined"
      density="compact"
      hide-details
      :menu-icon="ChevronDown"
      style="max-width: 220px"
      :menu-props="{ closeOnContentClick: true }"
    />

    <v-text-field
      v-model="text"
      placeholder="Search text"
      variant="outlined"
      density="compact"
      hide-details
      class="flex-grow-1"
    />

    <v-tooltip text="Remove condition">
      <template #activator="{ props: tooltipProps }">
        <v-btn
          v-bind="tooltipProps"
          icon
          variant="text"
          @click="remove('remove')"
        >
          <v-icon :icon="X" />
        </v-btn>
      </template>
    </v-tooltip>
  </div>
</template>
