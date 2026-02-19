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

    <!-- NEW: Форма редактирования -->
    <div class="profile-section">
      <h3>✏️ Редактирование данных</h3>
      <form @submit.prevent="handleUpdateProfile">
        <div class="form-row">
          <div class="form-group">
            <label>Имя *</label>
            <input
              v-model="profileForm.first_name"
              type="text"
              required
              :disabled="loadingProfile"
              placeholder="Ваше имя"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>Фамилия *</label>
            <input
              v-model="profileForm.last_name"
              type="text"
              required
              :disabled="loadingProfile"
              placeholder="Ваша фамилия"
              class="form-input"
            />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Email *</label>
            <input
              v-model="profileForm.email"
              type="email"
              required
              :disabled="loadingProfile"
              placeholder="example@company.com"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>Telegram ID *</label>
            <input
              v-model="profileForm.telegram_id"
              type="text"
              required
              :disabled="loadingProfile"
              placeholder="@username или числовой ID"
              class="form-input"
            />
          </div>
        </div>
        <button type="submit" class="btn-primary" :disabled="loadingProfile">
          {{ loadingProfile ? 'Сохранение...' : 'Сохранить изменения' }}
        </button>
        <p v-if="profileSuccess" class="success-message">{{ profileSuccess }}</p>
        <p v-if="profileError" class="error-message">{{ profileError }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/stores/auth'
import '@/assets/auth.css'

const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.user)
const userRole = computed(() => user.value?.role_name || 'Без роли')

const loadingProfile = ref(false)
const profileError = ref('')
const profileSuccess = ref('')

const profileForm = ref({
  first_name: '',
  last_name: '',
  email: '',
  telegram_id: ''
})

const handleUpdateProfile = async () => {
  console.log('Update profile:', profileForm.value)
}

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