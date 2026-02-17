import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/components/HeaderView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/components/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/components/RegisterView.vue'),
      meta: { guest: true },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/components/ProfileView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

export default router