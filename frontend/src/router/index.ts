import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '@/pages/HomePage.vue';
import SearchPage from '@/pages/SearchPage.vue';
import ProjectPage from '@/pages/ProjectPage.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/home',
    },
    {
      path: '/home',
      name: 'home',
      component: HomePage,
    },
    {
      path: '/search',
      name: 'search',
      component: SearchPage,
    },
    {
      path: '/projects/:projectId',
      name: 'project',
      component: ProjectPage,
      props: true,
    },
  ],
});

export default router;