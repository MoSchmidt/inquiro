import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '@/pages/HomePage.vue';
import LoginPage from '@/pages/LoginPage.vue';
import ProjectPapersPage from '@/pages/ProjectPapersPage.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
    },
    {
      path: '/projects/:projectId/papers',
      name: 'project-papers',
      component: ProjectPapersPage,
      props: true,
    },
  ],
});

export default router;
