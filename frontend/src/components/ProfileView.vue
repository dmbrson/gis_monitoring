<template>
  <div class="profile-container">
    <div class="profile-header">
      <h2>Профиль пользователя</h2>
      <button @click="handleLogout" class="btn-danger">Выйти</button>
    </div>

    <div class="profile-section">
      <h3>📋 Личная информация</h3>
      <div class="info-grid">
        <div class="info-item">
          <label>Имя пользователя:</label>
          <span>{{ user?.username }}</span>
        </div>
        <div class="info-item">
          <label>Роль:</label>
          <span class="role-badge">{{ userRole }}</span>
        </div>
        <div class="info-item">
          <label>Статус:</label>
          <span :class="['status-badge', user?.is_active ? 'active' : 'inactive']">
            {{ user?.is_active ? 'Активен' : 'Неактивен' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import '@/assets/auth.css'

const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.user)

const userRole = computed(() => {
  return user.value?.role_name || 'Без роли'
})

const handleLogout = async () => {
  if (authStore.isLoggingOut) return
  try {
    await authStore.logout()
    router.push('/login')
  } catch (e) {
    console.error('Logout failed:', e)
    router.push('/login')
  }
}
</script>

<style scoped>
</style>