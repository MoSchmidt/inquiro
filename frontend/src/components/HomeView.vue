<script setup lang="ts">
import { ref } from 'vue';
import { VLayout, VAppBar, VNavigationDrawer, VMain, VBtn, VIcon, VToolbarTitle, VContainer } from 'vuetify/components';
import { Menu as MenuIcon, FileText } from 'lucide-vue-next'; // Lucide Icons
import Sidebar from './Sidebar.vue';
import InputSection from './InputSection.vue';
import ResultsSection from './ResultsSection.vue';
import { Paper, Project } from './types'; // Importiere die Typen

import { useAuthStore } from '@/stores/auth';
import { login } from '@/services/auth';
import {AxiosError} from "axios";

// Zustand
const sidebarOpen = ref(false);
const currentQuery = ref<string | null>(null);
const outputs = ref<Paper[]>([]);
//const isLoggedIn = ref(false);

const errorMessage = ref<string | null>(null);
const isLoading = ref(false);
const authStore = useAuthStore();

const initialProjects: Project[] = [
  {
    id: '1',
    name: 'Project Alpha',
    query: 'Machine learning applications in healthcare',
    date: '2025-11-15',
    outputs: [
      { title: 'Deep Learning for Medical Image Analysis', author: 'Smith, J. et al.', year: 2024, url: 'https://example.com/paper1' },
      { title: 'AI-Driven Diagnosis Systems', author: 'Johnson, M. & Lee, K.', year: 2023, url: 'https://example.com/paper2' }
    ]
  },
  {
    id: '2',
    name: 'Project Beta',
    query: 'Climate change impacts on biodiversity',
    date: '2025-11-14',
    outputs: [
      { title: 'Global Warming Effects on Ecosystems', author: 'Brown, A. et al.', year: 2024, url: 'https://example.com/paper3' }
    ]
  },
  {
    id: '3',
    name: 'Project Gamma',
    query: 'Quantum computing advances',
    date: '2025-11-13',
    outputs: [
      { title: 'Quantum Algorithms for Optimization', author: 'Chen, L. & Wang, Y.', year: 2023, url: 'https://example.com/paper4' },
      { title: 'Quantum Algorithms for Optimization', author: 'Chen, L. & Wang, Y.', year: 2023, url: 'https://example.com/paper4' },
      { title: 'Quantum Algorithms for Optimization', author: 'Chen, L. & Wang, Y.', year: 2023, url: 'https://example.com/paper4' },
      { title: 'Quantum Algorithms for Optimization', author: 'Chen, L. & Wang, Y.', year: 2023, url: 'https://example.com/paper4' },
      { title: 'Quantum Algorithms for Optimization', author: 'Chen, L. & Wang, Y.', year: 2023, url: 'https://example.com/paper4' },
      { title: 'Quantum Algorithms for Optimization', author: 'Chen, L. & Wang, Y.', year: 2023, url: 'https://example.com/paper4' },
      { title: 'Quantum Algorithms for Optimization', author: 'Chen, L. & Wang, Y.', year: 2023, url: 'https://example.com/paper4' },
      { title: 'Quantum Algorithms for Optimization', author: 'Chen, L. & Wang, Y.', year: 2023, url: 'https://example.com/paper4' },
      { title: 'Quantum Algorithms for Optimization', author: 'Chen, L. & Wang, Y.', year: 2023, url: 'https://example.com/paper4' },
      { title: 'Quantum Algorithms for Optimization', author: 'Chen, L. & Wang, Y.', year: 2023, url: 'https://example.com/paper4' },
      { title: 'Quantum Algorithms for Optimization', author: 'Chen, L. & Wang, Y.', year: 2023, url: 'https://example.com/paper4' },
      { title: 'Quantum Algorithms for Optimization', author: 'Chen, L. & Wang, Y.', year: 2023, url: 'https://example.com/paper4' },
      { title: 'Quantum Algorithms for Optimization', author: 'Chen, L. & Wang, Y.', year: 2023, url: 'https://example.com/paper4' },
      { title: 'Quantum Algorithms for Optimization', author: 'Chen, L. & Wang, Y.', year: 2023, url: 'https://example.com/paper4' },
      { title: 'Quantum Algorithms for Optimization', author: 'Chen, L. & Wang, Y.', year: 2023, url: 'https://example.com/paper4' }
    ]
  }
];
const recentProjects = ref<Project[]>(initialProjects);

// Methoden
const handleSubmitQuery = (query: string) => {
  currentQuery.value = query;

  // Simuliere die Generierung von Artikeln
  const generatedOutputs: Paper[] = [
    { title: 'Recent Advances in Natural Language Processing', author: 'Anderson, P. & Martinez, R.', year: 2024, url: 'https://example.com/nlp-advances' },
    { title: 'Transformer Models: A Comprehensive Review', author: 'Davis, K. et al.', year: 2023, url: 'https://example.com/transformers' },
    { title: 'Attention Mechanisms in Neural Networks', author: 'Wilson, T. & Thompson, S.', year: 2024, url: 'https://example.com/attention' },
    { title: 'BERT and Beyond: Language Model Evolution', author: 'Garcia, M. et al.', year: 2023, url: 'https://example.com/bert' },
    { title: 'Large Language Models in Practice', author: 'Taylor, J. & White, L.', year: 2024, url: 'https://example.com/llm-practice' }
  ];
  outputs.value = generatedOutputs;

  // Füge zu den aktuellen Projekten hinzu
  const newProject: Project = {
    id: Date.now().toString(),
    name: `Project ${recentProjects.value.length + 1}`,
    query,
    date: new Date().toISOString().split('T')[0],
    outputs: generatedOutputs
  };
  recentProjects.value.unshift(newProject); // Füge am Anfang hinzu
};

const handleProjectSelect = (project: Project) => {
  currentQuery.value = project.query;
  outputs.value = project.outputs;
  sidebarOpen.value = false;
};

const handleNewQuery = () => {
  currentQuery.value = null;
  outputs.value = [];
};
/*
const handleLogin = (email: string, password: string) => {
  // Mock login logic
  isLoggedIn.value = true;
  sidebarOpen.value = false;
  console.log(`Logging in with: ${email} and ${password}`);
};
*/
const handleLogin = async (usernameFromSidebar: string) => {
  isLoading.value = true;
  errorMessage.value = null;

  try {
    const { access_token, refresh_token, user } = await login(usernameFromSidebar);

    authStore.setAuth({
      accessToken: access_token,
      refreshToken: refresh_token,
      user: user,
    });
    sidebarOpen.value = false;
  } catch (error: unknown) {
    const axiosError = error as AxiosError<{ detail?: string }>;

    if (axiosError.response?.data?.detail) {
      errorMessage.value = axiosError.response.data.detail;
    } else {
      errorMessage.value = 'An unexpected error occurred.';
    }
  } finally {
    isLoading.value = false;
  }
}
const handleLogout = () => {
  //isLoggedIn.value = false;
  authStore.clearAuth();
};
</script>

<template>
  <v-app>
    <v-layout>
      <v-navigation-drawer
          v-model="sidebarOpen"
          location="left"
          temporary
          width="320"
      >
        <Sidebar
            :is-open="sidebarOpen"
            :recent-projects="recentProjects"
            :is-logged-in="authStore.isAuthenticated"
            @close="sidebarOpen = false"
            @project-select="handleProjectSelect"
            @new-project="handleNewQuery"
            @login="handleLogin"
            @logout="handleLogout"
        />
      </v-navigation-drawer>

      <v-app-bar app color="white" flat border>
        <v-btn icon variant="text" @click="sidebarOpen = !sidebarOpen">
          <v-icon :icon="MenuIcon" />
        </v-btn>
        <v-toolbar-title class="text-h6">AI Text Processor</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn v-if="currentQuery" @click="handleNewQuery" variant="outlined" color="primary">
          Neue Abfrage
        </v-btn>
      </v-app-bar>

      <v-main class="bg-grey-lighten-4">
        <v-container fluid class="h-100">
          <div v-if="!currentQuery">
            <InputSection @submit="handleSubmitQuery" />
          </div>
          <div v-else>
            <ResultsSection :query="currentQuery" :outputs="outputs" />
          </div>
        </v-container>
      </v-main>
    </v-layout>
  </v-app>
</template>
<!--<script setup lang="ts">
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
</script>

<template>
  <h1>Hello, {{ authStore.user }}</h1>
  <p>{{ authStore.accessToken }}</p>
</template>

<style scoped></style>-->