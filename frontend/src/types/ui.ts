import type { Component } from 'vue';

export interface ActionMenuItem {
    title: string;
    value?: string; // Optional now, mostly for keys
    icon?: Component;
    color?: string;
    action?: () => void; // The logic lives here
    disabled?: boolean;
}