<script setup lang="ts">
import { ref, watch } from 'vue';
import { VBtn, VSelect, VTooltip, VDivider } from 'vuetify/components';
import ConditionRow from './ConditionRow.vue';
import type { ConditionGroup, TextCondition } from '@/types/search';
import { Plus, PlusSquare, Trash2 } from 'lucide-vue-next';

defineOptions({ name: 'AdvancedSearchGroup' });

const props = defineProps<{
  modelValue: ConditionGroup;
  removable?: boolean;
  /** Root renders without border/operator and is locked to AND */
  isRoot?: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: ConditionGroup): void;
  (e: 'remove'): void;
}>();

const clone = <T,>(v: T): T => JSON.parse(JSON.stringify(v));
const localGroup = ref<ConditionGroup>(clone(props.modelValue));

watch(() => props.modelValue, (val) => {
  // keep local shadow in sync but avoid shared refs
  localGroup.value = clone(val);
}, { deep: true });

watch(localGroup, (val) => {
  // always emit a fresh object (breaks shared refs between siblings/parents)
  emit('update:modelValue', clone(val));
}, { deep: true });

const logicalItems = [
  { title: 'All conditions (AND)', value: 'AND' },
  { title: 'Any condition (OR)',  value: 'OR'  },
];

function addCondition() {
  const next: TextCondition = {
    type: 'condition',
    field: 'title',
    operator: 'contains',
    value: '',
  };
  localGroup.value = { ...localGroup.value, children: [...localGroup.value.children, next] };
}

function addGroup() {
  const next: ConditionGroup = {
    type: 'group',
    operator: 'AND',
    children: [],
  };
  localGroup.value = { ...localGroup.value, children: [...localGroup.value.children, next] };
}

function removeChild(idx: number) {
  const children = localGroup.value.children.slice();
  children.splice(idx, 1);
  localGroup.value = { ...localGroup.value, children };
}

function updateChild(idx: number, updated: ConditionGroup | TextCondition) {
  const children = localGroup.value.children.slice();
  children[idx] = clone(updated);
  localGroup.value = { ...localGroup.value, children };
}
</script>

<template>
  <!-- Root: frameless; Nested: subtle card -->
  <div
    :class="[
      isRoot
        ? ''
        : 'rounded-lg border border-default pa-4 bg-surface',
    ]"
  >
    <!-- Header row: hidden for root; shown for nested -->
    <div
      v-if="!isRoot"
      class="d-flex align-center mb-3"
      style="gap: 12px"
    >
      <span class="text-medium-emphasis">Combine with</span>

      <v-select
        v-model="localGroup.operator"
        :items="logicalItems"
        item-title="title"
        item-value="value"
        variant="outlined"
        density="compact"
        hide-details
        style="max-width: 240px"
      />

      <v-tooltip text="Remove group">
        <template #activator="{ props: tprops }">
          <v-btn
            v-if="removable"
            v-bind="tprops"
            size="x-small"
            variant="text"
            :ripple="false"
            @click="$emit('remove')"
          >
            <v-icon :icon="Trash2" size="18" />
          </v-btn>
        </template>
      </v-tooltip>
    </div>

    <!-- Children -->
    <div class="ms-1">
      <div
        v-for="(child, idx) in localGroup.children"
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
        <v-divider v-if="idx < localGroup.children.length - 1" class="my-2" />
      </div>
    </div>

    <!-- Actions -->
    <div class="d-flex mt-3" style="gap: 8px">
      <v-btn size="small" variant="outlined" :ripple="false" @click="addCondition">
        <v-icon :icon="Plus" start /> Condition
      </v-btn>
      <v-btn size="small" variant="outlined" :ripple="false" @click="addGroup">
        <v-icon :icon="PlusSquare" start /> Group
      </v-btn>
    </div>
  </div>
</template>
