<template>
  <div class="object-create-page">
    <header class="page-header">
      <button @click="cancel" class="btn-back">← Назад</button>
      <h1>➕ Новый объект</h1>
      <div class="header-spacer"></div>
    </header>

    <div class="form-container">
      <form @submit.prevent="submitForm" class="form-panel">
        <div class="form-section">
          <h3>📋 Основная информация</h3>
          <div class="form-group">
            <label for="title">Название объекта *</label>
            <input id="title" type="text" class="form-input" placeholder="Например: Ремонт ЛЭП-10кВ" />
          </div>
          <div class="form-group">
            <label for="address">Адрес *</label>
            <input id="address" type="text" class="form-input" placeholder="г. Владивосток, ул. Светланская, 1" />
          </div>
          <div class="form-group">
            <label for="region">Район / Регион</label>
            <input id="region" type="text" class="form-input" placeholder="Первореченский, Фрунзенский..." />
          </div>
          <div class="form-group">
            <label for="description">Описание работ</label>
            <textarea id="description" class="form-textarea" rows="4" placeholder="Детали выполняемых работ..."></textarea>
          </div>
        </div>

        <div class="form-section">
          <h3>👥 Ответственные</h3>
          <div class="form-group">
            <label for="status_id">Статус *</label>
            <select id="status_id" class="form-select">
              <option value="" disabled>Выберите статус</option>
            </select>
          </div>
          <div class="form-group">
            <label for="responsible_id">Ответственный *</label>
            <select id="responsible_id" class="form-select">
              <option value="" disabled>Выберите сотрудника</option>
            </select>
          </div>
        </div>

        <div class="form-section">
          <h3>📅 Сроки работ</h3>
          <div class="form-row">
            <div class="form-group">
              <label for="start_date">Дата начала *</label>
              <input id="start_date" type="date" class="form-input" />
            </div>
            <div class="form-group">
              <label for="end_date">Дата окончания *</label>
              <input id="end_date" type="date" class="form-input" />
            </div>
          </div>
        </div>

        <div class="form-section">
          <h3>📍 Координаты</h3>
          <div class="coords-info">
            <span class="coords-label">Выбрано:</span>
            <span class="coords-placeholder">Кликните по карте для выбора</span>
          </div>
        </div>

        <div class="form-actions">
          <button type="button" @click="cancel" class="btn-secondary">Отмена</button>
          <button type="submit" class="btn-primary">Создать объект</button>
        </div>
      </form>

      <div class="map-panel">
        <div class="map-header">
          <span>Выберите местоположение</span>
          <small>Кликните по карте или перетащите маркер</small>
        </div>
        <div ref="mapContainer" class="map-wrapper"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
const cancel = () => {
  if (confirm('Отменить создание объекта?')) {
    history.back()
  }
}
const submitForm = () => {
  console.log('Form submitted (stub)')
}
</script>

<style scoped>
.object-create-page {
  min-height: 100vh;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  position: sticky;
  top: 0;
  z-index: 20;
}

.btn-back {
  background: #f1f3f5;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  color: #495057;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: background 0.2s;
}

.btn-back:hover {
  background: #e2e6ea;
}

.page-header h1 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
}

.header-spacer {
  flex: 1;
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
</style>