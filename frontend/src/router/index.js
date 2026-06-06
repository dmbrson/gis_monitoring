import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import MainLayout from '@/components/layout/MainLayout.vue'
import AuthLayout from '@/components/layout/AuthLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: MainLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('@/components/MapDashboardView.vue')
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/components/ProfileView.vue')
        },
        {
          path: 'objects/create',
          name: 'object-create',
          component: () => import('@/components/ObjectCreateView.vue'),
          meta: { adminOnly: true }
        },
        {
          path: 'objects/:id',
          name: 'object-detail',
          component: () => import('@/components/ObjectDetailView.vue')
        }
      ]
    },
    {
      path: '/login',
      component: AuthLayout,
      name: 'login',
      component: () => import('@/components/LoginView.vue'),
      meta: { guest: true }
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  if (authStore.accessToken && !authStore.user && !to.meta.guest) {
    try {
      await authStore.fetchUser()
    } catch (e) {
      console.warn('Не удалось загрузить данные пользователя:', e)
    }
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next('/profile')
  } else if (to.meta.adminOnly) {
    const userRole = authStore.user?.role?.name
    const isSuperuser = authStore.user?.is_superuser
    if (userRole !== 'admin' && !isSuperuser) {
      next('/')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router