<template>
  <div class="map-dashboard">
    <aside class="filters-panel">
      <div class="filters-header">
        <h3>Фильтры</h3>
        <button @click="resetFilters" class="btn-reset" title="Сбросить все фильтры">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 4 23 10 17 10"></polyline>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
          </svg>
        </button>
      </div>

      <div class="filter-group">
        <label for="search">Поиск</label>
        <input
          id="search"
          v-model="filters.search"
          @input="onFilterChange"
          type="text"
          placeholder="Название, адрес, код..."
          class="form-input"
        />
      </div>

      <div class="filter-group">
        <label for="status">Статус</label>
        <select
          id="status"
          v-model="filters.status"
          @change="onFilterChange"
          class="form-select"
        >
          <option value="">Все статусы</option>
          <option v-for="status in statuses" :key="status.id" :value="status.id">
            {{ status.name }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label for="region">Регион / Район</label>
        <input
          id="region"
          v-model="filters.region"
          @input="onFilterChange"
          type="text"
          placeholder="Например: Первореченский"
          class="form-input"
        />
      </div>

      <div class="filter-group">
        <label>Период работ</label>
        <div class="date-range">
          <input v-model="filters.start_date" @change="onFilterChange" type="date" class="form-input" />
          <span class="date-separator">—</span>
          <input v-model="filters.end_date" @change="onFilterChange" type="date" class="form-input" />
        </div>
      </div>

      <div class="legend" v-if="statuses.length">
        <h4>Статусы</h4>
        <div v-for="status in statuses" :key="status.id" class="legend-item">
          <span class="legend-color" :style="{ backgroundColor: status.color }"></span>
          <span class="legend-name">{{ status.name }}</span>
        </div>
      </div>
    </aside>

    <main class="map-container" ref="mapContainer">
      <transition name="fade">
        <div v-if="loading" class="map-overlay">
          <div class="spinner"></div>
          <p>Загрузка объектов...</p>
        </div>
      </transition>

      <transition name="fade">
        <div v-if="error" class="map-overlay error">
          <p class="error-text">{{ error }}</p>
          <button @click="fetchData" class="btn-retry">Повторить</button>
        </div>
      </transition>

      <div class="map-hint" v-if="!loading && objectsCount === 0">
        <p>Объекты не найдены</p>
        <small>Попробуйте изменить фильтры или добавить новый объект</small>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore, api } from '@/stores/auth'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { escapeHtml } from '@/utils/sanitize'

const router = useRouter()
const authStore = useAuthStore()

const MAP_STYLE = `https://api.maptiler.com/maps/019c7f1e-1822-7283-9a47-54edeb6ca98d/style.json?key=${import.meta.env.VITE_MAPTILER_KEY}`
const VLADIVOSTOK_CENTER = [131.8853, 43.1155]
const DEFAULT_ZOOM = 12

const map = ref(null)
const mapContainer = ref(null)
const markers = ref([])
const objects = ref([])
const statuses = ref([])
const loading = ref(true)
const error = ref(null)
const objectsCount = ref(0)

const filters = ref({
  status: '',
  responsible: '',
  region: '',
  start_date: '',
  end_date: '',
  search: ''
})

const isAdmin = computed(() => {
  return authStore.user?.role?.name === 'admin' || authStore.user?.is_superuser === true
})

const createNewObject = () => {
  router.push({ name: 'object-create' })
}

let abortController = null

const fetchObjects = async () => {
  if (abortController) abortController.abort()
  abortController = new AbortController()

  try {
    const params = {}
    Object.entries(filters.value).forEach(([key, val]) => {
      if (val && val !== '') params[key] = val
    })

    const response = await api.get('/api/objects/', {
      params,
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

    objects.value = data
    objectsCount.value = response.data.count ?? data.length

    if (map.value && map.value.loaded()) {
      updateMarkers()
    }
  } catch (err) {
    if (err.name === 'AbortError') return
    console.error('Ошибка загрузки объектов:', err)
    error.value = err.response?.data?.detail || 'Не удалось загрузить объекты'
  }
}

const fetchStatuses = async () => {
  try {
    const response = await api.get('/api/statuses/')

    let data = []
    if (Array.isArray(response.data)) {
      data = response.data
    } else if (response.data?.results && Array.isArray(response.data.results)) {
      data = response.data.results
    }

    statuses.value = data
  } catch (err) {
    console.warn('Статусы не загружены:', err)
    statuses.value = []
  }
}

const fetchData = async () => {
  loading.value = true
  error.value = null
  await Promise.all([fetchObjects(), fetchStatuses()])
  loading.value = false
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

    map.value.on('load', () => {
      updateMarkers()
    })
  } catch (err) {
    console.error('Ошибка инициализации карты:', err)
    error.value = 'Не удалось загрузить карту'
    loading.value = false
  }
}

const createMarkerElement = (color, isActive = true) => {
  const el = document.createElement('div')
  el.className = 'map-marker'

  el.style.cssText = `
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background-color: ${color};
    border: 3px solid white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    cursor: ${isActive ? 'pointer' : 'default'};
    will-change: transform;
    position: absolute;
  `

  el.innerHTML = '<span style="display:block;width:100%;height:100%;border-radius:50%"></span>'

  if (isActive) {
    el.onmouseenter = () => { el.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)' }
    el.onmouseleave = () => { el.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)' }
  }
  return el
}

const updateMarkers = () => {
  if (!map.value || !map.value.loaded() || !Array.isArray(objects.value)) {
    console.warn('updateMarkers: карта не готова или данные не массив')
    return
  }

  markers.value.forEach(marker => marker.remove())
  markers.value = []

  objects.value.forEach(obj => {
    if (!obj?.coordinates || !Array.isArray(obj.coordinates) || obj.coordinates.length !== 2) return
    const [lng, lat] = obj.coordinates
    const statusColor = /^#[0-9a-f]{6}$/i.test(obj.status?.color) ? obj.status.color : '#6c757d'
    const statusName = escapeHtml(obj.status?.name || 'Без статуса')

    const el = createMarkerElement(statusColor)

    const popup = new maplibregl.Popup({
      offset: 20,
      closeButton: true,
      closeOnClick: false
    }).setHTML(`
      <div class="marker-popup">
        <strong>${escapeHtml(obj.title)}</strong><br>
        <small class="address">${escapeHtml(obj.address)}</small><br>
        <div class="status-badge" style="color: ${statusColor}">● ${statusName}</div>
        ${obj.code ? `<small class="code">${escapeHtml(obj.code)}</small>` : ''}
      </div>
    `)

    const marker = new maplibregl.Marker({ element: el, anchor: 'center', offset: [0, -14] })
      .setLngLat([lng, lat])
      .setPopup(popup)
      .addTo(map.value)

    el.addEventListener('click', (e) => {
      e.stopPropagation()
      router.push({ name: 'object-detail', params: { id: obj.id } })
    })

    markers.value.push(marker)
  })
}

let searchTimeout = null

const onFilterChange = () => {
  if (filters.value.search) {
    clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => {
      fetchData()
    }, 400)
  } else {
    fetchData()
  }
}

const resetFilters = () => {
  filters.value = {
    status: '',
    responsible: '',
    region: '',
    start_date: '',
    end_date: '',
    search: ''
  }
  fetchData()
}

watch(
  () => objects.value,
  () => {
    if (map.value && map.value.loaded()) {
      updateMarkers()
    }
  },
  { deep: true }
)

onMounted(async () => {
  initMap()
  await fetchData()
})

onUnmounted(() => {
  if (abortController) abortController.abort()
  clearTimeout(searchTimeout)
  markers.value.forEach(marker => marker.remove())
  if (map.value) {
    map.value.remove()
    map.value = null
  }
})
</script>

<style scoped>
.map-dashboard {
  display: flex;
  height: 100%;
  width: 100%;
  background: #f8f9fa;
  position: relative;
  overflow: hidden;
}

.filters-panel {
  width: 358px;
  min-width: 280px;
  background: white;
  border-right: 1px solid #e0e0e0;
  padding: 16px 20px;
  overflow-y: auto;
  z-index: 10;
  box-shadow: 2px 0 12px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex-shrink: 0;
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  margin-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.filters-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 0.85rem;
}

.btn-reset {
  background: #f1f3f5;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-reset:hover {
  background: #e2e6ea;
  color: #333;
}

.filter-group {
  margin-bottom: 4px;
}

.filter-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #495057;
  font-size: 0.85rem;
}

.form-input,
.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.95rem;
  background: white;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #0d6efd;
  box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.15);
}

.date-range {
  display: flex;
  gap: 8px;
  align-items: center;
}

.date-separator {
  color: #adb5bd;
  font-weight: 300;
}

.legend {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.legend h4 {
  margin: 0 0 12px 0;
  font-size: 0.85rem;
  font-weight: 600;
  color: #2c3e50;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 0;
  font-size: 0.9rem;
  color: #555;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  flex-shrink: 0;
}

.map-container {
  flex: 1;
  position: relative;
  background: #e9ecef;
  min-width: 0;
  min-height: 0;
}

.map-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255,255,255,0.95);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 20;
  gap: 16px;
}

.map-overlay.error {
  background: rgba(255, 248, 248, 0.98);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e9ecef;
  border-top-color: #0d6efd;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-text {
  color: #dc3545;
  font-weight: 500;
  text-align: center;
  padding: 0 20px;
  margin: 0;
}

.btn-retry {
  background: #0d6efd;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  transition: background 0.2s;
}

.btn-retry:hover {
  background: #0b5ed7;
}

.map-hint {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 20px 32px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  text-align: center;
  z-index: 5;
}

.map-hint p {
  margin: 0 0 6px 0;
  font-weight: 500;
  color: #495057;
}

.map-hint small {
  color: #6c757d;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .map-dashboard {
    flex-direction: column;
  }

  .filters-panel {
    width: 100%;
    max-height: 45vh;
    border-right: none;
    border-bottom: 1px solid #e0e0e0;
  }

  .map-container {
    height: 55vh;
    flex: none;
  }
}

@media (max-width: 480px) {
  .filters-panel {
    padding: 12px 16px;
  }

  .date-range {
    flex-direction: column;
    align-items: stretch;
    gap: 4px;
  }

  .date-separator {
    display: none;
  }
}
</style>