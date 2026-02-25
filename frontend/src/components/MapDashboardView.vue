<template>
  <div class="map-dashboard">
    <aside class="filters-panel">
      <div class="filters-header">
        <h3>🔍 Фильтры</h3>
        <button @click="resetFilters" class="btn-reset" title="Сбросить все фильтры">⟲</button>
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
          <input v-model="filters.start_date" @change="onFilterChange" type="date" class="form-input" title="Дата начала" />
          <span class="date-separator">—</span>
          <input v-model="filters.end_date" @change="onFilterChange" type="date" class="form-input" title="Дата окончания" />
        </div>
      </div>

      <div class="legend" v-if="statuses.length">
        <h4>📋 Статусы</h4>
        <div v-for="status in statuses" :key="status.id" class="legend-item">
          <span class="legend-color" :style="{ backgroundColor: status.color }" :title="status.description"></span>
          <span class="legend-name">{{ status.name }}</span>
        </div>
      </div>
    </aside>

    <main class="map-container" ref="mapContainer">
      <div class="create-object-btn" v-if="isAdmin">
        <button @click="createNewObject" class="btn-primary" title="Добавить новый объект">
          <span class="btn-icon">+</span>
          <span class="btn-text">Объект</span>
        </button>
      </div>

      <div class="objects-count" v-if="!loading && !error">
        📍 {{ objectsCount }} объектов
      </div>

      <div class="map-hint" v-if="!loading && objectsCount === 0">
        <p>Объекты не найдены</p>
        <small>Попробуйте изменить фильтры или добавить новый объект</small>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const mapContainer = ref(null)
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

const fetchObjects = async () => {
  console.log('🔄 Загрузка объектов (заглушка)')
  objects.value = []
  objectsCount.value = 0
}

const fetchStatuses = async () => {
  console.log('🔄 Загрузка статусов (заглушка)')
  statuses.value = [
    { id: 1, name: 'Новый', color: '#17a2b8' },
    { id: 2, name: 'В работе', color: '#ffc107' },
    { id: 3, name: 'Завершён', color: '#28a745' }
  ]
}

const fetchData = async () => {
  loading.value = true
  error.value = null
  await Promise.all([fetchObjects(), fetchStatuses()])
  loading.value = false
}

const onFilterChange = () => {
  console.log('🔍 Фильтры изменены:', filters.value)
  fetchData()
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

onMounted(async () => {
  console.log('Компонент смонтирован')
  await fetchData()
})

onUnmounted(() => {
  console.log('Компонент размонтирован')
})
</script>


<style scoped>
.map-dashboard {
  display: flex;
  height: calc(100vh - 64px);
  background: #f8f9fa;
  position: relative;
}
.filters-panel {
  width: 340px;
  min-width: 280px;
  background: white;
  border-right: 1px solid #e0e0e0;
  padding: 16px 20px;
  overflow-y: auto;
  z-index: 10;
  box-shadow: 2px 0 12px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
  gap: 8px;
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
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
}
.btn-reset {
  background: #f1f3f5;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.1rem;
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
  font-size: 0.9rem;
}
.form-input,
.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.95rem;
  background: white;
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
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
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
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  flex-shrink: 0;
}
.map-container {
  flex: 1;
  position: relative;
  background: #e9ecef;
}
.objects-count {
  position: absolute;
  top: 16px;
  right: 16px;
  background: white;
  padding: 8px 16px;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
  font-size: 0.9rem;
  font-weight: 500;
  color: #333;
  z-index: 5;
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
.create-object-btn {
  position: absolute;
  bottom: 24px;
  left: 24px;
  z-index: 10;
}
.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #0d6efd;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(13, 110, 253, 0.3);
}
.btn-icon {
  font-size: 1.2rem;
  font-weight: bold;
}
@media (max-width: 900px) {
  .map-dashboard { flex-direction: column; }
  .filters-panel {
    width: 100%;
    max-height: 45vh;
    border-right: none;
    border-bottom: 1px solid #e0e0e0;
  }
  .map-container { height: 55vh; }
}
@media (max-width: 480px) {
  .filters-panel { padding: 12px 16px; }
  .date-range { flex-direction: column; align-items: stretch; gap: 4px; }
  .date-separator { display: none; }
  .btn-text { display: none; }
  .btn-primary { padding: 12px; border-radius: 50%; }
}
</style>