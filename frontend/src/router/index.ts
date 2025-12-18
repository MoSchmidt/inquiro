import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '@/pages/HomePage.vue';
import SearchPage from '@/pages/SearchPage.vue';
import ProjectPage from '@/pages/ProjectPage.vue';
import { useAuthStore } from '@/stores/auth';

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

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  // If trying to access a project page AND not logged in
  if (to.name === 'project' && !authStore.isAuthenticated) {
    // Redirect to home/search
    next({ name: 'home' });
  } else {
    next();
  }
});

export default router;
