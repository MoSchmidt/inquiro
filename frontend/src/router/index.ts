import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../components/HomeView.vue';
import LoginView from '../components/LoginView.vue';
import { useAuthStore } from '@/stores/auth';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      //meta: { requiresAuth: true },
    }, /*
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    }, */
  ],
});
/*
router.beforeEach((to, from, next) => {
  const auth = useAuthStore();

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({ name: 'login' });
  } else if (to.name === 'login' && auth.isAuthenticated) {
    next({ name: 'home' });
  } else {
    next();
  }
}); */

export default router;
