import type { ConditionGroup, TextCondition } from '@/api';

export type { ConditionGroup, TextCondition };

export interface AdvancedSearchOptions {
  yearFrom?: number;
  yearTo?: number;
  root: ConditionGroup;
}