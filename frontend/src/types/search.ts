export type TextField = 'title' | 'abstract';
export type MatchOperator = 'contains' | 'not_contains';

export interface TextCondition {
  type: 'condition';
  field: TextField;
  operator: MatchOperator;
  value: string;
}

export interface ConditionGroup {
  type: 'group';
  operator: 'AND' | 'OR';
  children: (TextCondition | ConditionGroup)[];
}

export interface AdvancedSearchOptions {
  yearFrom?: number;
  yearTo?: number;
  root: ConditionGroup;
}