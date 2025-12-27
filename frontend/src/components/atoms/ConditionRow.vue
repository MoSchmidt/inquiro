<script setup lang="ts">
import { VBtn, VSelect, VTextField, VTooltip } from 'vuetify/components';
import type { TextCondition } from '@/types/search';
import { X } from 'lucide-vue-next';

const props = defineProps<{ modelValue: TextCondition }>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: TextCondition): void;
  (e: 'remove'): void;
}>();

const update = (patch: Partial<TextCondition>) => {
  emit('update:modelValue', { ...props.modelValue, ...patch });
};

const fieldItems = [
  { title: 'Title',    value: 'title' },
  { title: 'Abstract', value: 'abstract' },
];

const operatorItems = [
  { title: 'Contains',          value: 'contains' },
  { title: 'Does not contain',  value: 'not_contains' },
];
</script>

<template>
  <div class="d-flex align-center" style="gap: 12px">
    <v-select
      :items="fieldItems"
      item-title="title"
      item-value="value"
      :model-value="modelValue.field"
      variant="outlined"
      density="compact"
      hide-details
      style="max-width: 180px"
      @update:model-value="(v) => update({ field: v as any })"
    />

    <v-select
      :items="operatorItems"
      item-title="title"
      item-value="value"
      :model-value="modelValue.operator"
      variant="outlined"
      density="compact"
      hide-details
      style="max-width: 220px"
      @update:model-value="(v) => update({ operator: v as any })"
    />

    <v-text-field
      :model-value="modelValue.value"
      placeholder="Search text"
      variant="outlined"
      density="compact"
      hide-details
      class="flex-grow-1"
      @update:model-value="(v) => update({ value: v })"
    />

    <v-tooltip text="Remove condition">
      <template #activator="{ props: tprops }">
        <v-btn v-bind="tprops" icon variant="text" :ripple="false" @click="emit('remove')">
          <v-icon :icon="X" />
        </v-btn>
      </template>
    </v-tooltip>
  </div>
</template>
