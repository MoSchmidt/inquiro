<script setup lang="ts">
import { computed } from 'vue';
import { VBtn, VDivider, VIcon, VSelect, VTooltip } from 'vuetify/components';
import { ChevronDown, Plus, PlusSquare, Trash2 } from 'lucide-vue-next';

import ConditionRow from './ConditionRow.vue';
import type { ConditionGroup, TextCondition } from '@/types/search';

defineOptions({ name: 'AdvancedSearchGroup' });

const props = defineProps<{
  modelValue: ConditionGroup;
  removable?: boolean;
  isRoot?: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: ConditionGroup): void;
  (e: 'remove'): void;
}>();

const model = computed<ConditionGroup>({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
});

const logicalItems = [
  { title: 'All conditions (AND)', value: 'AND' },
  { title: 'Any condition (OR)', value: 'OR' },
] as const;

const operatorModel = computed<ConditionGroup['operator']>({
  get: () => (props.isRoot ? 'AND' : model.value.operator),
  set: (op) => {
    if (props.isRoot) return; // root is locked to AND
    model.value = { ...model.value, operator: op };
  },
});

function addCondition() {
  const next: TextCondition = {
    type: 'condition',
    field: 'title',
    operator: 'contains',
    value: '',
  };
  model.value = { ...model.value, children: [...model.value.children, next] };
}

function addGroup() {
  const next: ConditionGroup = {
    type: 'group',
    operator: 'AND',
    children: [],
  };
  model.value = { ...model.value, children: [...model.value.children, next] };
}

function removeChild(index: number) {
  model.value = {
    ...model.value,
    children: model.value.children.filter((_, i) => i !== index),
  };
}

function updateChild(index: number, updated: ConditionGroup | TextCondition) {
  model.value = {
    ...model.value,
    children: model.value.children.map((c, i) => (i === index ? updated : c)),
  };
}
</script>

<template>
  <!-- Root: frameless; Nested: subtle card -->
  <div
    :class="[
      'advanced-search-group',
      !isRoot && 'rounded-lg border border-default pa-4 bg-surface',
    ]"
  >
    <!-- Header row (hidden for root) -->
    <div
      v-if="!isRoot"
      class="d-flex align-center mb-3 group-header"
    >
      <span class="text-medium-emphasis">Combine with</span>

      <v-select
        v-model="operatorModel"
        :items="logicalItems"
        item-title="title"
        item-value="value"
        variant="outlined"
        density="compact"
        hide-details
        :menu-icon="ChevronDown"
        class="operator-select"
        :menu-props="{ closeOnContentClick: true }"
      />

      <v-tooltip text="Remove group">
        <template #activator="{ props: tprops }">
          <v-btn
            v-if="removable"
            v-bind="tprops"
            size="x-small"
            variant="text"
            @click="emit('remove')"
          >
            <v-icon :icon="Trash2" size="18" />
          </v-btn>
        </template>
      </v-tooltip>
    </div>

    <!-- Children -->
    <div class="ms-1">
      <div
        v-for="(child, idx) in model.children"
        :key="idx"
        class="mb-2"
      >
        <AdvancedSearchGroup
          v-if="child.type === 'group'"
          :model-value="child"
          :removable="true"
          :is-root="false"
          @update:model-value="(val) => updateChild(idx, val)"
          @remove="removeChild(idx)"
        />

        <ConditionRow
          v-else
          :model-value="child"
          @update:model-value="(val) => updateChild(idx, val)"
          @remove="removeChild(idx)"
        />

        <v-divider v-if="idx < model.children.length - 1" class="my-2" />
      </div>
    </div>

    <!-- Actions -->
    <div class="d-flex mt-3 actions-row">
      <v-btn
        size="small"
        variant="outlined"
        @click="addCondition"
      >
        <v-icon :icon="Plus" start /> Condition
      </v-btn>

      <v-btn
        size="small"
        variant="outlined"
        @click="addGroup"
      >
        <v-icon :icon="PlusSquare" start /> Group
      </v-btn>
    </div>
  </div>
</template>

<style scoped>
.group-header {
  gap: 12px;
}

.operator-select {
  max-width: 240px;
}

.actions-row {
  gap: 8px;
}
</style>
