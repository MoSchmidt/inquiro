import { useDark, useToggle } from '@vueuse/core';
import { useTheme as useVuetifyTheme } from 'vuetify';
import { watch } from 'vue';

export function useTheme() {
    const vuetifyTheme = useVuetifyTheme();

    // 1. Initialize useDark
    // By default, this toggles the 'dark' class on the <html> tag.
    // This handles TAILWIND automatically.
    const isDark = useDark({
        selector: 'html',
        attribute: 'class',
        valueDark: 'dark',
        valueLight: '',
    });

    // 2. Create the toggle function
    const toggleTheme = useToggle(isDark);

    // 3. Sync Vuetify with VueUse
    // Whenever isDark changes (by click, system pref, or storage), update Vuetify.
    watch(
        isDark,
        (val) => {
            vuetifyTheme.global.name.value = val ? 'dark' : 'light';
        },
        { immediate: true } // Run immediately on load to set initial Vuetify state
    );

    return {
        isDark,
        toggleTheme,
    };
}