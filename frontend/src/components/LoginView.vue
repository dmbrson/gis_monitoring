<template>
  <div class="auth-container">
    <h2>Вход</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label>Имя пользователя</label>
        <input v-model="username" type="text" required />
      </div>
      <div class="form-group">
        <label>Пароль</label>
        <input v-model="password" type="password" required />
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? 'Вход...' : 'Войти' }}
      </button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
    <p class="auth-links">
      Нет учётной записи? Обратитесь к администратору
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  try {
    await authStore.login(username.value, password.value)
    router.push('/profile')
  } catch (e) {
    if (e.response?.data?.detail) {
      error.value = e.response.data.detail
    } else if (e.response?.data?.non_field_errors) {
      error.value = e.response.data.non_field_errors.join(', ')
    } else if (typeof e.response?.data === 'string') {
      error.value = e.response.data
    } else {
      error.value = 'Ошибка входа. Проверьте логин и пароль'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
</style>