import type { Component } from 'vue';

export interface ActionMenuItem {
    title: string;
    value?: string | number;
    icon?: Component;
    color?: string;
    action?: () => void;
    disabled?: boolean;
    hidden?: boolean;
}