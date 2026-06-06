<template>
  <div class="dashboard-layout">
    <aside class="nav-sidebar">
      <div class="nav-header">
        <div class="logo">ГИС</div>
      </div>

      <nav class="nav-menu">
        <div class="nav-item" :class="{ active: isActive('/') }" @click="$router.push('/')" title="Карта объектов">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9 22 9 12 15 12 15 22"></polyline>
          </svg>
          <span class="nav-text">Карта</span>
        </div>

        <div class="nav-item" :class="{ active: isActive('/profile') }" @click="$router.push('/profile')" title="Профиль">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
          <span class="nav-text">Профиль</span>
        </div>

        <div class="nav-item" v-if="isAdmin" @click="createNewObject" title="Создать объект">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          <span class="nav-text">Создать</span>
        </div>
      </nav>

      <div class="nav-footer">
        <div class="nav-item" @click="logout" title="Выйти">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16 17 21 12 16 7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
          <span class="nav-text">Выход</span>
        </div>
      </div>
    </aside>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isAdmin = computed(() => {
  return authStore.user?.role?.name === 'admin' || authStore.user?.is_superuser
})

const isActive = (path) => {
  return route.path === path
}

const createNewObject = () => {
  router.push({ name: 'object-create' })
}

const logout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  height: 100vh;
  height: 100dvh;
  width: 100%;
  background: #f8f9fa;
  position: relative;
}

.main-content {
  flex: 1;
  position: relative;
  overflow: auto;
  min-height: 0;
}

.main-content.map-page {
  overflow: hidden;
}

.nav-sidebar {
  width: 64px;
  min-width: 64px;
  background: white;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  padding: 12px 8px;
  gap: 8px;
  z-index: 11;
  flex-shrink: 0;
}

.nav-header {
  padding: 8px 0 16px 0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 8px;
}

.logo {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #0d6efd 0%, #0dcaf0 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 0.85rem;
  margin: 0 auto;
  box-shadow: 0 2px 8px rgba(13, 110, 253, 0.3);
}

.nav-menu {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 10px 8px;
  border-radius: 8px;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.7rem;
  min-height: 56px;
}

.nav-item:hover {
  background: #f8f9fa;
  color: #0d6efd;
}

.nav-item.active {
  background: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
}

.nav-item svg {
  opacity: 0.8;
}

.nav-text {
  font-weight: 500;
  text-align: center;
  line-height: 1.1;
}

.nav-footer {
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.main-content {
  flex: 1;
  position: relative;
}

@media (max-width: 768px) {
  .dashboard-layout {
    flex-direction: column;
  }

  .nav-sidebar {
    width: 100%;
    height: auto;
    flex-direction: row;
    padding: 8px 12px;
    border-right: none;
    border-bottom: 1px solid #e0e0e0;
    overflow-x: auto;
  }

  .nav-header {
    display: none;
  }

  .nav-menu {
    flex-direction: row;
    gap: 4px;
  }

  .nav-item {
    min-height: 48px;
    padding: 8px 12px;
  }

  .nav-footer {
    display: none;
  }
}

@media (max-width: 480px) {
  .nav-text {
    display: none;
  }

  .nav-item {
    min-height: 48px;
    padding: 8px;
  }
}
</style>