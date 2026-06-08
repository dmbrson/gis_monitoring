<template>
  <div class="object-create-page">
    <div class="form-container">
      <form @submit.prevent="submitForm" class="form-panel">

        <transition name="fade">
          <div v-if="error" class="form-error global">
            ⚠️ {{ error }}
          </div>
        </transition>

        <transition name="fade">
          <div v-if="submitting" class="form-overlay">
            <div class="spinner"></div>
            <p>Создание объекта...</p>
          </div>
        </transition>

        <div class="form-section">
          <div class="form-group">
            <label for="title">Название объекта *</label>
            <input
              id="title"
              v-model="form.title"
              type="text"
              class="form-input"
              :class="{ 'input-error': errors.title }"
              placeholder="Например: Ремонт ЛЭП-10кВ"
            />
            <span v-if="errors.title" class="form-error">{{ errors.title }}</span>
          </div>
          <div class="form-group">
            <label for="address">Адрес *</label>
            <input
              id="address"
              v-model="form.address"
              type="text"
              class="form-input"
              :class="{ 'input-error': errors.address }"
              placeholder="г. Владивосток, ул. Светланская, 1"
            />
            <span v-if="errors.address" class="form-error">{{ errors.address }}</span>
          </div>

          <div class="form-group">
            <label for="region">Район / Регион</label>
            <input
              id="region"
              v-model="form.region"
              type="text"
              class="form-input"
              placeholder="Первореченский, Фрунзенский..."
              title="Укажите район или регион выполнения работ"
              :disabled="submitting"
            />
          </div>

          <div class="form-group">
            <label for="description">Описание работ</label>
            <textarea
              id="description"
              v-model="form.description"
              class="form-textarea"
              rows="4"
              placeholder="Детали выполняемых работ..."
              :disabled="submitting"
            ></textarea>
          </div>
        </div>

        <div class="form-section">
          <h3>Ответственный</h3>
          <div class="form-group">
            <label for="status_id">Статус *</label>
            <select
              id="status_id"
              v-model="form.status_id"
              class="form-select"
              :class="{ 'input-error': errors.status_id }"
              title="Выберите текущий статус объекта"
              :disabled="submitting || !statuses.length"
            >
              <option value="" disabled>Выберите статус</option>
              <option
                v-for="status in statuses"
                :key="status.id"
                :value="status.id"
              >
                {{ status.name }}
              </option>
            </select>
            <span v-if="errors.status_id" class="form-error">{{ errors.status_id }}</span>
          </div>
          <div class="form-group">
            <label for="responsible_id">Ответственный *</label>
            <select
              id="responsible_id"
              v-model="form.responsible_id"
              class="form-select"
              :class="{ 'input-error': errors.responsible_id }"
              title="Назначьте сотрудника, ответственного за объект"
              :disabled="submitting || !users.length"
            >
              <option value="" disabled>Выберите сотрудника</option>
              <option
                v-for="user in users"
                :key="user.id"
                :value="user.id"
              >
                {{ user.display_name || user.full_name || user.role }}
              </option>
            </select>
            <span v-if="errors.responsible_id" class="form-error">{{ errors.responsible_id }}</span>
          </div>
        </div>

        <div class="form-section">
          <h3>Сроки работ</h3>
          <div class="form-row">
            <div class="form-group">
              <label for="start_date">Дата начала *</label>
              <input
                id="start_date"
                v-model="form.start_date"
                type="date"
                class="form-input"
                :class="{ 'input-error': errors.start_date }"
                title="Укажите планируемую дату начала работ"
                :disabled="submitting"
              />
              <span v-if="errors.start_date" class="form-error">{{ errors.start_date }}</span>
            </div>
            <div class="form-group">
              <label for="end_date">Дата окончания *</label>
              <input
                id="end_date"
                v-model="form.end_date"
                type="date"
                class="form-input"
                :class="{ 'input-error': errors.end_date }"
                title="Укажите планируемую дату завершения работ"
                :disabled="submitting"
              />
              <span v-if="errors.end_date" class="form-error">{{ errors.end_date }}</span>
            </div>
          </div>
        </div>

        <div class="form-section">
              <h3>Главное фото</h3>
              <div class="form-group">
                <label for="main_photo">Загрузить фото</label>

                <div v-if="photoPreview" class="photo-preview">
                  <img :src="photoPreview" alt="Preview" class="preview-image" />
                  <button type="button" @click="clearPhoto" class="btn-remove-photo" title="Удалить фото">×</button>
                </div>

                <input
                  id="main_photo"
                  type="file"
                  accept="image/*"
                  @change="handlePhotoUpload"
                  class="form-file-input"
                  :disabled="submitting"
                />
                <small class="text-secondary">
                  Допустимые форматы: JPG, PNG, WEBP. Макс. размер: 10 МБ
                </small>
                <span v-if="errors.main_photo" class="form-error">{{ errors.main_photo }}</span>
              </div>
            </div>

        <div class="form-section">
          <h3>Координаты</h3>
          <div class="coords-info">
            <span class="coords-label">Выбрано:</span>
            <span v-if="form.coordinates" class="coords-value">
              {{ form.coordinates[1].toFixed(5) }}, {{ form.coordinates[0].toFixed(5) }}</span>
            <span v-else class="coords-placeholder">Кликните по карте для выбора</span>
          <span v-if="errors.coordinates" class="form-error">{{ errors.coordinates }}</span>
          </div>
        </div>

        <div class="form-actions">
          <button
            type="button"
            @click="cancel"
            class="btn-secondary"
            :disabled="submitting"
            title="Отменить создание и вернуться назад"
          >
            <span class="btn-text">Отмена</span>
          </button>

          <button
            type="submit"
            class="btn-primary"
            :disabled="submitting"
            title="Сохранить новый объект в системе"
          >
            <span class="btn-text">{{ submitting ? 'Создание...' : 'Создать объект' }}</span>
          </button>
        </div>
      </form>

      <div class="map-panel">
        <div class="map-header">
          <span>Выберите местоположение</span>
          <small>Кликните по карте или перетащите маркер</small>
        </div>

        <transition name="fade">
          <div v-if="error && !submitting" class="map-overlay error">
            <p class="error-text">⚠️ {{ error }}</p>
            <button @click="initMap" class="btn-retry" :disabled="loading">
              <span class="btn-icon">⟲</span>
              <span class="btn-text">Повторить</span>
            </button>
          </div>
        </transition>

        <transition name="fade">
          <div v-if="loading && !submitting" class="map-overlay">
            <div class="spinner"></div>
            <p>Загрузка карты...</p>
          </div>
        </transition>
        <div ref="mapContainer" class="map-wrapper"></div>
      </div>
    </div>

    <transition name="fade">
      <div v-if="showCropper" class="cropper-modal">
        <div class="cropper-modal-content">
          <div class="cropper-header">
            <h3>Обрежьте фото (16/9)</h3>
            <button @click="cancelCrop" class="btn-close" type="button">×</button>
          </div>

          <div class="cropper-wrapper">
            <Cropper
              ref="cropperRef"
              :src="tempImage"
              :stencil-props="{
                aspectRatio: 16 / 9
              }"
              :resize-image="{ adjustStencil: false }"
              :wheel-resize="true"
              class="cropper"
            />
          </div>

          <div class="cropper-actions">
            <button @click="cancelCrop" class="btn-secondary" type="button">
              Отмена
            </button>
            <button @click="applyCrop" class="btn-primary" type="button">
              Применить
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore, api } from '@/stores/auth'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { Cropper } from 'vue-advanced-cropper'
import 'vue-advanced-cropper/dist/style.css'

const router = useRouter()
const authStore = useAuthStore()

const MAP_STYLE = `https://api.maptiler.com/maps/019c7f1e-1822-7283-9a47-54edeb6ca98d/style.json?key=${import.meta.env.VITE_MAPTILER_KEY}`
const VLADIVOSTOK_CENTER = [131.8853, 43.1155]
const DEFAULT_ZOOM = 12

const map = ref(null)
const mapContainer = ref(null)
const markers = ref([])
const loading = ref(false)
const error = ref(null)
const submitting = ref(false)

const form = ref({
  title: '',
  address: '',
  region: '',
  coordinates: null,
  description: '',
  status_id: null,
  responsible_id: null,
  start_date: '',
  end_date: '',
  main_photo: null
})

const statuses = ref([])
const users = ref([])
const errors = ref({})
const photoPreview = ref(null)

const showCropper = ref(false)
const tempImage = ref(null)
const cropperRef = ref(null)
const croppedFile = ref(null)

let abortController = null

const isAdmin = computed(() => {
  return authStore.user?.role?.name === 'admin' || authStore.user?.is_superuser === true
})

const fetchStatuses = async () => {
  try {
    const response = await api.get('/api/statuses/')

    let data = []
    if (Array.isArray(response.data)) {
      data = response.data
    } else if (response.data?.results && Array.isArray(response.data.results)) {
      data = response.data.results
    } else if (response.data?.objects && Array.isArray(response.data.objects)) {
      data = response.data.objects
    }

    statuses.value = data

    if (statuses.value.length && !form.value.status_id) {
      form.value.status_id = statuses.value[0].id
    }
  } catch (err) {
    if (err.name === 'AbortError') return
    console.warn('Не удалось загрузить статусы:', err)
  }
}

const fetchUsers = async () => {
  if (abortController) abortController.abort()
  abortController = new AbortController()

  try {
    const response = await api.get('/api/auth/users/', {
      params: {
        limit: 100,
        ordering: 'last_name,first_name'
      },
      signal: abortController.signal
    })

    let data = []
    if (Array.isArray(response.data)) {
      data = response.data
    } else if (response.data?.results && Array.isArray(response.data.results)) {
      data = response.data.results
    } else if (response.data?.objects && Array.isArray(response.data.objects)) {
      data = response.data.objects
    }

    users.value = data.filter(u => u.is_active !== false)
  } catch (err) {
    if (err.name === 'AbortError') return
    console.warn('Не удалось загрузить пользователей:', err)
    users.value = []
  }
}

const fetchData = async () => {
  loading.value = true
  error.value = null
  await Promise.all([fetchStatuses(), fetchUsers()])
  loading.value = false
}

const createMarkerElement = (color = '#dc3545', isDraggable = true) => {
  const el = document.createElement('div')
  el.className = 'create-marker'
  el.style.cssText = `
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background-color: ${color};
    border: 3px solid white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    cursor: ${isDraggable ? 'move' : 'default'};
    will-change: auto;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  `

  if (isDraggable) {
    el.onmouseenter = () => { el.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)' }
    el.onmouseleave = () => { el.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)' }
  }

  return el
}

const initMap = () => {
  if (map.value) return

  try {
    map.value = new maplibregl.Map({
      container: mapContainer.value,
      style: MAP_STYLE,
      center: VLADIVOSTOK_CENTER,
      zoom: DEFAULT_ZOOM,
      pitch: 0,
      bearing: 0
    })

    map.value.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'top-right')
    map.value.addControl(new maplibregl.GeolocateControl({
      positionOptions: { enableHighAccuracy: true },
      trackUserLocation: true
    }), 'top-right')

    map.value.on('click', async (e) => {
      const { lng, lat } = e.lngLat
      setMarker([lng, lat])
      await reverseGeocode(lng, lat)
    })

    map.value.on('load', () => {
      if (markers.value[0]) {
        markers.value[0].setDraggable(true)
        markers.value[0].on('dragend', async () => {
          const lngLat = markers.value[0].getLngLat()
          form.value.coordinates = [lngLat.lng, lngLat.lat]
          await reverseGeocode(lngLat.lng, lngLat.lat)
        })
      }
    })
  } catch (err) {
    console.error('Ошибка инициализации карты:', err)
    error.value = 'Не удалось загрузить карту'
    loading.value = false
  }
}

const setMarker = (coordinates) => {
  const [lng, lat] = coordinates

  markers.value.forEach(marker => marker.remove())
  markers.value = []

  const el = createMarkerElement('#dc3545', true)

  const marker = new maplibregl.Marker({
    element: el,
    anchor: 'center',
    offset: [0, -14]
  })
    .setLngLat([lng, lat])
    .addTo(map.value)

  markers.value.push(marker)
  form.value.coordinates = [lng, lat]
}

const reverseGeocode = async (lng, lat) => {
  try {
    const url = `https://api.maptiler.com/geocoding/${lng},${lat}.json?key=${import.meta.env.VITE_MAPTILER_KEY}&language=ru`
    const res = await fetch(url)
    const data = await res.json()

    if (data.features?.[0]) {
      const feature = data.features[0]
      const context = feature.context || []

      const address = feature.place_name?.split(',')[0] || ''
      const region = context.find(c => c.id?.includes('region'))?.text ||
                     context.find(c => c.id?.includes('district'))?.text || ''

      const addressInput = document.getElementById('address')
      const regionInput = document.getElementById('region')

      if (!addressInput?.matches(':focus')) {
        form.value.address = address
      }
      if (!regionInput?.matches(':focus')) {
        form.value.region = region
      }
    }
  } catch (e) {
    console.warn('Reverse geocoding failed:', e)
  }
}

const validateForm = () => {
  errors.value = {}

  if (!form.value.title?.trim()) errors.value.title = 'Название обязательно'
  if (!form.value.address?.trim()) errors.value.address = 'Адрес обязателен'
  if (!form.value.coordinates || form.value.coordinates.length !== 2) {
    errors.value.coordinates = 'Выберите точку на карте'
  }
  if (!form.value.status_id) errors.value.status_id = 'Выберите статус'
  if (!form.value.responsible_id) errors.value.responsible_id = 'Выберите ответственного'
  if (!form.value.start_date) errors.value.start_date = 'Укажите дату начала'
  if (!form.value.end_date) errors.value.end_date = 'Укажите дату окончания'

  if (form.value.start_date && form.value.end_date &&
      form.value.end_date < form.value.start_date) {
    errors.value.end_date = 'Дата окончания не может быть раньше начала'
  }

  return Object.keys(errors.value).length === 0
}

const handlePhotoUpload = (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  const validTypes = ['image/jpeg', 'image/png', 'image/webp']
  if (!validTypes.includes(file.type)) {
    errors.value.main_photo = 'Только JPG, PNG или WEBP'
    event.target.value = ''
    return
  }

  if (file.size > 10 * 1024 * 1024) {
    errors.value.main_photo = 'Максимальный размер: 10 МБ'
    event.target.value = ''
    return
  }

  errors.value.main_photo = null

  const reader = new FileReader()
  reader.onload = (e) => {
    tempImage.value = e.target.result
    showCropper.value = true
  }
  reader.readAsDataURL(file)
}

const cancelCrop = () => {
  showCropper.value = false
  tempImage.value = null
  const input = document.getElementById('main_photo')
  if (input) input.value = ''
}

const applyCrop = async () => {
  if (!cropperRef.value) return

  try {
    const { coordinates } = cropperRef.value.getResult()
    const canvas = document.createElement('canvas')

    const width = Math.round(coordinates.width)
    const height = Math.round(coordinates.height)

    canvas.width = width
    canvas.height = height

    const ctx = canvas.getContext('2d')
    const image = new Image()

    await new Promise((resolve, reject) => {
      image.onload = resolve
      image.onerror = reject
      image.src = tempImage.value
    })

    ctx.drawImage(
      image,
      coordinates.left,
      coordinates.top,
      coordinates.width,
      coordinates.height,
      0,
      0,
      width,
      height
    )

    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.9))

    const file = new File([blob], 'cropped-photo.jpg', {
      type: 'image/jpeg',
      lastModified: Date.now()
    })

    croppedFile.value = file
    form.value.main_photo = file

    const reader = new FileReader()
    reader.onload = (e) => {
      photoPreview.value = e.target.result
    }
    reader.readAsDataURL(file)

    showCropper.value = false
    tempImage.value = null

  } catch (err) {
    console.error('Ошибка при обрезке:', err)
    errors.value.main_photo = 'Не удалось обработать изображение'
  }
}

const clearPhoto = () => {
  form.value.main_photo = null
  croppedFile.value = null
  photoPreview.value = null
  const input = document.getElementById('main_photo')
  if (input) input.value = ''
}

const submitForm = async () => {
  if (!validateForm()) {
    const firstError = document.querySelector('.form-error')
    firstError?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    return
  }

  submitting.value = true
  error.value = null

  try {
    const formData = new FormData()

    Object.entries(form.value).forEach(([key, value]) => {
      if (key === 'main_photo' && value instanceof File) {
        formData.append('main_photo', value)
      } else if (key === 'coordinates' && value) {
        formData.append('coordinates_input', JSON.stringify(value))
      } else if (value !== null && value !== undefined && value !== '') {
        formData.append(key, value)
      }
    })

    await api.post('/api/objects/',  formData)

    router.push({ name: 'home' })
    alert('Объект успешно создан!')

  } catch (err) {
    console.error('Ошибка создания объекта:', err)

    if (err.response?.data) {
      errors.value = err.response.data
      error.value = 'Проверьте правильность заполнения формы'
    } else {
      error.value = 'Не удалось создать объект. Проверьте соединение.'
    }
  } finally {
    submitting.value = false
  }
}

const cancel = () => {
  if (confirm('Отменить создание объекта?')) {
    router.back()
  }
}

onMounted(async () => {
  if (!isAdmin.value) {
    router.push('/')
    return
  }

  initMap()
  await fetchData()
})

onUnmounted(() => {
  if (abortController) abortController.abort()
  markers.value.forEach(marker => marker.remove())
  if (map.value) {
    map.value.remove()
    map.value = null
  }
})
</script>

<style scoped>
.object-create-page {
  min-height: 100vh;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
}

.page-header h1 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
}


.form-container {
  display: flex;
  flex: 1;
  gap: 0;
  overflow: hidden;
}

.form-panel {
  width: 480px;
  min-width: 380px;
  background: white;
  padding: 24px;
  overflow-y: auto;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-section {
  padding: 16px 0;
  border-bottom: 1px solid #eee;
}

.form-section:last-child {
  border-bottom: none;
}

.form-section h3 {
  margin: 0 0 16px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #495057;
  font-size: 0.95rem;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.95rem;
  background: white;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #0d6efd;
  box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.15);
}

.form-input.input-error,
.form-select.input-error,
.form-textarea.input-error {
  border-color: #dc3545;
}

.form-error {
  display: block;
  margin-top: 4px;
  font-size: 0.85rem;
  color: #dc3545;
  font-weight: 500;
}

.form-error.global {
  background: #fff5f5;
  padding: 12px;
  border-radius: 6px;
  border-left: 4px solid #dc3545;
  margin-top: 8px;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
}

.coords-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  font-family: monospace;
  font-size: 0.9rem;
}

.coords-label {
  color: #6c757d;
}

.coords-value {
  color: #2c3e50;
  font-weight: 500;
}

.coords-placeholder {
  color: #adb5bd;
  font-style: italic;
}

.form-actions {
  display: flex;
  gap: 12px;
  padding-top: 20px;
  margin-top: auto;
}

.btn-primary,
.btn-secondary {
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-primary {
  background: #0d6efd;
  color: white;
  flex: 1;
}

.btn-primary:hover:not(:disabled) {
  background: #0b5ed7;
}

.btn-primary:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.7;
}

.btn-secondary {
  background: #f1f3f5;
  color: #495057;
}

.btn-secondary:hover {
  background: #e2e6ea;
}

.map-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #e9ecef;
}

.map-header {
  padding: 12px 16px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.map-header span {
  font-weight: 500;
  color: #2c3e50;
}

.map-header small {
  color: #6c757d;
  font-size: 0.85rem;
}

.map-wrapper {
  flex: 1;
  min-height: 400px;
}

@media (max-width: 1100px) {
  .form-container {
    flex-direction: column;
  }

  .form-panel {
    width: 100%;
    max-height: 60vh;
    border-right: none;
    border-bottom: 1px solid #e0e0e0;
  }

  .map-panel {
    height: 40vh;
  }
}

@media (max-width: 480px) {
  .form-panel {
    padding: 16px;
  }

  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn-primary, .btn-secondary {
    width: 100%;
  }
}

.photo-preview {
  position: relative;
  width: 200px;
  height: 150px;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 12px;
  border: 2px solid #e9ecef;
  background: #f8f9fa;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.btn-remove-photo {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(220, 53, 69, 0.9);
  color: white;
  border: none;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.btn-remove-photo:hover {
  background: #dc3545;
}

.form-file-input {
  width: 100%;
  padding: 8px;
  border: 1px dashed #ced4da;
  border-radius: 6px;
  background: white;
  font-size: 0.9rem;
  cursor: pointer;
}

.form-file-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.text-secondary {
  color: #6c757d;
  font-size: 0.85rem;
  display: block;
  margin-top: 4px;
}

.cropper-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.cropper-modal-content {
  background: white;
  border-radius: 12px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.cropper-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.cropper-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #2c3e50;
}

.btn-close {
  background: none;
  border: none;
  font-size: 2rem;
  color: #6c757d;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.btn-close:hover {
  background: #f1f3f5;
  color: #2c3e50;
}

.cropper-wrapper {
  flex: 1;
  padding: 24px;
  background: #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  max-height: 60vh;
  overflow: auto;
}

.cropper {
  max-width: 100%;
  max-height: 100%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.cropper-actions {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e0e0e0;
  background: white;
}

.cropper-actions .btn-primary,
.cropper-actions .btn-secondary {
  flex: 1;
}

:deep(.cropper__wrapper) {
  max-width: 100%;
  max-height: 100%;
}

:deep(.cropper__stencil) {
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5);
}

:deep(.cropper__image) {
  max-width: 100%;
  max-height: 100%;
}
</style>