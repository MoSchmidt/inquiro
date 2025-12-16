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
          background: '#F9FAFB',
          surface: '#FFFFFF',
          primary: '#0065bd',
          secondary: '#005293',
          accent: '#64a0c8',
          error: '#EF4444',
          info: '#3B82F6',
          success: '#10B981',
          warning: '#F59E0B',
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
          primary: '#0065bd',
          secondary: '#005293',
          accent: '#64a0c8',
          error: '#F87171',
          info: '#60A5FA',
          success: '#34D399',
          warning: '#FBBF24',
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
