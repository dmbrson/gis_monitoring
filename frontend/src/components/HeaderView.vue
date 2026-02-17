<template>
  <header class="header">
    <nav>
      <router-link to="/">Главная</router-link>

      <template v-if="authStore.isAuthenticated">
        <span>{{ authStore.user?.username }}</span>
        <button @click="handleLogout" class="logout-btn">
          Выйти
        </button>
      </template>

      <template v-else>
        <router-link to="/login">Войти</router-link>
      </template>
    </nav>
  </header>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
</style>