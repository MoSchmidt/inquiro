<script setup lang="ts">
import { VIcon } from 'vuetify/components';
import { ChevronDown } from 'lucide-vue-next';

defineProps<{
  expanded: boolean;
  size?: number;
}>();
</script>

<template>
  <VIcon
    :icon="ChevronDown"
    :size="size ?? 18"
    class="expansion-chevron"
    :class="{ 'expansion-chevron--expanded': expanded }"
  />
</template>

<style scoped>
.expansion-chevron {
  transition: transform 0.18s ease;
}
.expansion-chevron--expanded {
  transform: rotate(180deg);
}
</style>
