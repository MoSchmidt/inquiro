import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import { aliases, mdi } from 'vuetify/iconsets/mdi';

const defaultFont = 'Inter, Roboto, Arial, sans-serif';

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: {
          background: '#F3F4F6',
          surface: '#FFFFFF',

          primary: '#0065bd',
          secondary: '#005293',
          error: '#EF4444',
          info: '#3B82F6',
          success: '#10B981',
          warning: '#F59E0B',

          // Custom Semantic Colors
          'step-surface': '#E3F2FD',
          'step-text': '#1976D2',
          'success-surface': '#F1F8E9',
          'snackbar-success': '#10B981',

          // Borders
          'border-light': '#E0E0E0',
          'border-highlight': '#BBDEFB',
          'success-border': '#8BC34A',
        },
        variables: {
          'font-family': defaultFont,
        },
      },
      dark: {
        dark: true,
        colors: {
          background: '#0F172A',
          surface: '#1E293B',

          primary: '#60A5FA',
          secondary: '#7DD3FC',

          error: '#F87171',
          info: '#60A5FA',
          success: '#34D399',
          warning: '#FBBF24',

          // Custom Semantic Colors
          'step-surface': '#0f172a',
          'step-text': '#60A5FA',
          'success-surface': '#064e3b',
          'snackbar-success': '#2E7D32',

          // Borders
          'border-light': '#334155',
          'border-highlight': '#1e40af',
          'success-border': '#15803d',
        },
        variables: {
          'font-family': defaultFont,
        },
      },
    },
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  defaults: {
    global: {
      ripple: false,
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable',
    },
    VBtn: {
      color: 'primary',
      rounded: 'lg',
    },
    VCard: {
      rounded: 'lg',
    },
    VDataTable: {
      density: 'comfortable',
    },
  },
});