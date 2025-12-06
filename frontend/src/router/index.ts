import { createRouter, createWebHistory } from 'vue-router';
import SearchPage from '@/pages/SearchPage.vue';
import ProjectPage from '@/pages/ProjectPage.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/search',
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
