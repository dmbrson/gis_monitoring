<template>
  <div class="object-detail">
    <header class="detail-header">
      <button @click="$router.back()" class="btn-back" title="Назад">←</button>
      <div class="header-info">
        <h2>{{ object?.title || 'Загрузка...' }}</h2>
        <span v-if="object?.code" class="object-code">{{ object.code }}</span>
      </div>
      <div class="header-actions">
        <span
          v-if="object?.status"
          class="status-badge"
          :style="{ backgroundColor: object.status.color + '20', color: object.status.color }"
        >
          {{ object.status.name }}
        </span>
        <button
          v-if="canChangeStatus"
          @click="openStatusModal"
          class="btn-primary btn-sm"
          :disabled="loading"
        >Сменить статус
        </button>
      </div>
    </header>

    <section class="main-photo" v-if="object">
      <div class="photo-container">
        <img
          :src="mainPhotoUrl"
          :alt="object.title"
          class="main-image"
          @click="openPhotoModal(mainPhotoUrl)"
        />
        <div v-if="!mainPhotoUrl" class="photo-placeholder">
          <span>📷</span>
          <small>Фото не загружено</small>
        </div>
      </div>
      <div class="photo-gallery" v-if="photoPreviews.length">
        <img
          v-for="(photo, idx) in photoPreviews"
          :key="idx"
          :src="photo"
          class="gallery-thumb"
          @click="openPhotoModal(photo)"
        />
      </div>
    </section>

    <section class="info-grid" v-if="object">
      <div class="info-item">
        <label>Адрес</label>
        <p>{{ object.address }}</p>
        <p v-if="object.region" class="text-secondary">{{ object.region }}</p>
      </div>

      <div class="info-item">
        <label>Координаты</label>
        <p>{{ coordinatesFormatted }}</p>
        <a
          v-if="object.coordinates"
          :href="mapLink"
          target="_blank"
          class="link-small"
        >
          Открыть на карте →
        </a>
      </div>

      <div class="info-item">
        <label>Ответственный</label>
        <p>{{ responsibleName }}</p>
        <p v-if="object.responsible?.role" class="text-secondary">
          {{ roleLabels[object.responsible.role.name] || object.responsible.role.name }}
        </p>
      </div>

      <div class="info-item">
        <label>Период работ</label>
        <p :class="{ 'text-danger': isOverdue }">
          {{ formatDate(object.start_date) }} — {{ formatDate(object.end_date) }}
          <span v-if="isOverdue" class="badge-danger">Просрочено</span>
        </p>
      </div>

      <div class="info-item full-width">
        <label>Описание работ</label>
        <p class="description">{{ object.description || 'Нет описания' }}</p>
      </div>
    </section>

    <section class="timeline-section" v-if="object">
      <h3>История объекта</h3>

      <div v-if="timelineLoading" class="timeline-loading">
        <div class="spinner-sm"></div>
        <small>Загрузка истории...</small>
      </div>

      <div v-else-if="mergedTimeline.length === 0" class="timeline-empty">
        <p>История пуста</p>
      </div>

      <div v-else class="timeline">
        <div
          v-for="item in mergedTimeline"
          :key="item.id + '_' + item.type"
          class="timeline-item"
        >
          <div class="timeline-marker" :class="item.type"></div>
          <div class="timeline-content">
            <div class="timeline-header">
              <span class="timeline-date">{{ formatDateTime(item.created_at || item.changed_at) }}</span>
              <span class="timeline-author">
                <span v-if="item.is_bot" class="bot-badge" title="Отправлено через Max-бота"></span>
                {{ item.author_name || item.changed_by_name || 'Система' }}
              </span>
            </div>

            <div v-if="item.type === 'status_change'" class="status-change">
              <small>Статус изменён:</small>
              <div class="status-transition">
                <span class="status-old">{{ item.old_value || '—' }}</span>
                <span class="arrow">→</span>
                <span class="status-new" :style="{ color: item.new_status_color }">{{ item.new_value }}</span>
              </div>
            </div>

            <div v-else-if="item.type === 'comment'" class="comment-text">
              {{ item.text }}
            </div>

            <div v-if="item.photos?.length" class="comment-photos">
              <img
                v-for="(photo, idx) in item.photos"
                :key="idx"
                :src="photo"
                class="comment-photo"
                @click="openPhotoModal(photo)"
              />
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="comment-form-section" v-if="object">
      <h4>Добавить комментарий</h4>
      <form @submit.prevent="submitComment" class="comment-form">
        <textarea
          v-model="newComment"
          placeholder="Например: 'Залили фундамент, фото приложено'"
          class="form-input"
          rows="3"
          :disabled="submittingComment"
        ></textarea>

        <div class="comment-actions">
          <button type="button" class="btn-icon" title="Прикрепить фото" disabled>
            📎
          </button>
          <small class="text-secondary">📎 Фото можно прикрепить через Max-бота</small>
          <button type="submit" class="btn-primary" :disabled="submittingComment || !newComment.trim()">
            {{ submittingComment ? 'Отправка...' : 'Отправить' }}
          </button>
        </div>
      </form>
    </section>

    <div v-if="showStatusModal" class="modal-overlay" @click.self="closeStatusModal">
      <div class="modal">
        <h4>Сменить статус</h4>
        <select v-model="newStatusId" class="form-select">
          <option v-for="status in statuses" :key="status.id" :value="status.id">
            {{ status.name }}
          </option>
        </select>
        <div class="modal-actions">
          <button @click="closeStatusModal" class="btn-secondary">Отмена</button>
          <button @click="confirmStatusChange" class="btn-primary" :disabled="!newStatusId || statusLoading">
            {{ statusLoading ? 'Сохранение...' : 'Подтвердить' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="showPhotoModal" class="modal-overlay photo-modal" @click.self="closePhotoModal">
      <button class="modal-close" @click="closePhotoModal">×</button>
      <img :src="currentPhoto" class="modal-image" alt="Preview" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore, api } from '@/stores/auth'
import { escapeHtml } from '@/utils/sanitize'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const object = ref(null)
const statuses = ref([])
const history = ref([])
const comments = ref([])
const loading = ref(true)
const timelineLoading = ref(false)
const submittingComment = ref(false)
const statusLoading = ref(false)

const showStatusModal = ref(false)
const showPhotoModal = ref(false)
const currentPhoto = ref('')
const newStatusId = ref(null)
const statusChangeComment = ref('')
const newComment = ref('')

const authUser = computed(() => authStore.user)

const isAdmin = computed(() =>
  authUser.value?.role?.name === 'admin' || authUser.value?.is_superuser
)

const isManager = computed(() =>
  authUser.value?.role?.name === 'manager'
)

const isMaster = computed(() =>
  authUser.value?.role?.name === 'master'
)

const canChangeStatus = computed(() => {
  if (!object.value || !authUser.value) return false
  if (isAdmin.value || isManager.value) return true
  if (isMaster.value && object.value.responsible?.id === authUser.value.id) return true
  return false
})

const coordinatesFormatted = computed(() => {
  if (!object.value?.coordinates || !Array.isArray(object.value.coordinates)) return '—'
  const [lng, lat] = object.value.coordinates
  return `${lat?.toFixed(5) || '—'}, ${lng?.toFixed(5) || '—'}`
})

const mapLink = computed(() => {
  if (!object.value?.coordinates) return '#'
  const [lng, lat] = object.value.coordinates
  return `https://www.openstreetmap.org/?mlat=${lat}&mlon=${lng}#map=15/${lat}/${lng}`
})

const responsibleName = computed(() => {
  if (!object.value?.responsible) return '—'
  const { first_name, last_name, username } = object.value.responsible
  return `${last_name || ''} ${first_name || ''}`.trim() || username || '—'
})

const mainPhotoUrl = computed(() => {
  if (object.value?.main_photo_url) {
    return object.value.main_photo_url
  }
  return null
})

const photoPreviews = computed(() => {
  return []
})

const isOverdue = computed(() => {
  if (!object.value?.end_date) return false
  const end = new Date(object.value.end_date)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return end < today && object.value.status?.name !== 'Завершён'
})

const roleLabels = {
  admin: 'Администратор',
  manager: 'Менеджер',
  master: 'Мастер'
}

const mergedTimeline = computed(() => {
  const items = []

  if (Array.isArray(history.value)) {
    history.value.forEach(h => {
      const changedByName = h.changed_by
        ? `${h.changed_by.last_name || ''} ${h.changed_by.first_name || ''}`.trim() || h.changed_by.username
        : 'Система'

      items.push({
        id: h.id,
        type: 'status_change',
        changed_at: h.changed_at,
        changed_by_name: changedByName,
        field_name: h.field_name,
        old_value: h.old_value,
        new_value: h.new_value,
        new_status_color: h.new_status_color,
        is_bot: h.is_bot || false
      })
    })
  }

  if (Array.isArray(comments.value)) {
    comments.value.forEach(c => {
      const authorName = c.author
        ? `${c.author.last_name || ''} ${c.author.first_name || ''}`.trim() || c.author.username
        : 'Неизвестно'

      items.push({
        id: c.id,
        type: 'comment',
        created_at: c.created_at,
        author_name: authorName,
        text: c.text,
        photos: c.photos || [],
        is_bot: c.is_bot || false
      })
    })
  }

  return items.sort((a, b) => {
    const dateA = new Date(a.created_at || a.changed_at)
    const dateB = new Date(b.created_at || b.changed_at)
    return dateB - dateA
  })
})

const fetchData = async () => {
  const id = route.params.id
  loading.value = true

  try {
    const { data: obj } = await api.get(`/api/objects/${id}/`)
    object.value = obj
    newStatusId.value = obj.status?.id

    const { data: statusList } = await api.get('/api/statuses/')
    statuses.value = Array.isArray(statusList) ? statusList : (statusList.results || [])

    timelineLoading.value = true
    const [historyRes, commentsRes] = await Promise.all([
      api.get(`/api/objects/${id}/history/`),
      api.get(`/api/objects/${id}/comments/`)
    ])

    history.value = historyRes.data?.results || historyRes.data || []
    comments.value = commentsRes.data?.results || commentsRes.data || []

  } catch (err) {
    console.error('Ошибка загрузки данных:', err)
  } finally {
    loading.value = false
    timelineLoading.value = false
  }
}

const submitComment = async () => {
  if (!newComment.value.trim() || !object.value) return

  submittingComment.value = true
  try {
    await api.post('/api/comments/', {
      object: object.value.id,
      text: newComment.value.trim()
    })
    newComment.value = ''
    const { data } = await api.get(`/api/objects/${object.value.id}/comments/`)
    comments.value = data?.results || data || []
  } catch (err) {
    console.error('Ошибка отправки комментария:', err)
  } finally {
    submittingComment.value = false
  }
}

const openStatusModal = () => {
  newStatusId.value = object.value?.status?.id
  statusChangeComment.value = ''
  showStatusModal.value = true
}

const closeStatusModal = () => {
  showStatusModal.value = false
}

const confirmStatusChange = async () => {
  if (!newStatusId.value || !object.value) return

  statusLoading.value = true
  try {
    await api.patch(`/api/objects/${object.value.id}/update_status/`, {
      status_id: newStatusId.value,
      comment: statusChangeComment.value.trim() || undefined
    })
    const { data } = await api.get(`/api/objects/${object.value.id}/`)
    object.value = data
    closeStatusModal()
  } catch (err) {
    console.error('Ошибка смены статуса:', err)
  } finally {
    statusLoading.value = false
  }
}

const openPhotoModal = (url) => {
  currentPhoto.value = url
  showPhotoModal.value = true
}

const closePhotoModal = () => {
  showPhotoModal.value = false
  currentPhoto.value = ''
}

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    year: 'numeric', month: 'long', day: 'numeric'
  })
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString('ru-RU', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
</style>