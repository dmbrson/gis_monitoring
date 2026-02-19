import { defineStore } from 'pinia'
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Интерцептор для добавления токена
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Интерцептор для обновления токена
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    const isAuthEndpoint = originalRequest.url?.includes('/api/auth/token/refresh/') ||
                           originalRequest.url?.includes('/api/auth/login/') ||
                           originalRequest.url?.includes('/api/auth/logout/')

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken) {
        originalRequest._retry = true

        try {
          const { data } = await api.post('/api/auth/token/refresh/', {
            refresh: refreshToken,
          })

          localStorage.setItem('access_token', data.access)
          localStorage.setItem('refresh_token', data.refresh)

          if (window.authStore) {
            window.authStore.accessToken = data.access
            window.authStore.refreshToken = data.refresh
          }

          originalRequest.headers.Authorization = `Bearer ${data.access}`
          return api(originalRequest)

        } catch (refreshError) {
          console.warn('Refresh failed, logging out:', refreshError.response?.data)

          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')

          if (window.authStore) {
            window.authStore.clearTokens()
          }

          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }

          return Promise.reject(refreshError)
        }
      }
    }

    return Promise.reject(error)
  }
)

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: localStorage.getItem('access_token'),
    refreshToken: localStorage.getItem('refresh_token'),
    isLoggingOut: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    needsVerification: (state) => state.user?.needs_password_change === true,
  },

  actions: {
    async login(username, password) {
      const { data } = await api.post('/api/auth/login/', { username, password })
      this.setTokens(data)
      this.user = data.user
      return data
    },

    async logout() {
      if (this.isLoggingOut) return
      this.isLoggingOut = true

      const tokenToBlacklist = this.refreshToken
      const accessToken = this.accessToken

      try {
        if (tokenToBlacklist) {
          await api.post(
            '/api/auth/logout/',
            { refresh: tokenToBlacklist }
          )
        }
      } catch (e) {
        console.log('Logout API response:', e.response?.status || 'Network Error')
      } finally {
        this.clearTokens()
        this.isLoggingOut = false
      }
    },

    async fetchUser() {
      try {
        const { data } = await api.get('/api/auth/user/')
        this.user = data
      } catch {
        this.clearTokens()
      }
    },

    setTokens(data) {
      this.accessToken = data.access
      this.refreshToken = data.refresh
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
    },

    clearTokens() {
      this.accessToken = null
      this.refreshToken = null
      this.user = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    },
  },
})
export let authStoreInstance = null

export const initAuthStore = (store) => {
  authStoreInstance = store
  window.authStore = store
}

export { api }