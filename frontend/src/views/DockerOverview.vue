<template>
  <AppShell>
    <div class="dashboard docker-page">
      <div class="card glass control-panel">
        <div class="panel-row">
          <div class="panel-text">
            <p class="panel-label">Docker 服务</p>
            <p class="panel-subtitle">
              {{ panelSubtitle }}
            </p>
          </div>
          <div class="panel-actions">
            <button class="icon-button" @click="loadOverview" :disabled="overviewLoading" title="刷新">
              ⟳
            </button>
            <button class="primary-button" @click="startCreate">新增服务</button>
          </div>
        </div>
        <div v-if="summary" class="metrics-row">
          <div class="metric-chip">
            <span>总计</span>
            <strong>{{ summary.total }}</strong>
          </div>
          <div class="metric-chip metric-chip--ok">
            <span>在线</span>
            <strong>{{ summary.online }}</strong>
          </div>
          <div class="metric-chip">
            <span>运行中</span>
            <strong>{{ summary.running }}</strong>
          </div>
          <div class="metric-chip metric-chip--warn">
            <span>异常</span>
            <strong>{{ summary.unhealthy }}</strong>
          </div>
        </div>
      </div>

      <div v-if="overviewError" class="dash-status dash-status--error">
        获取 Docker 状态失败：{{ overviewError.message }}
      </div>

      <div v-if="dockerServices.length" class="services-grid">
        <DockerServiceCard
          v-for="svc in dockerServices"
          :key="svc.slug"
          :service="svc"
          @edit="startEdit"
        />
      </div>
      <p v-else class="empty-hint">暂无 Docker 配置或服务不可用。</p>

      <teleport to="body">
        <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
          <div class="modal">
            <header class="modal-header">
              <h3>{{ isEditing ? '编辑服务' : '添加新服务' }}</h3>
              <button class="modal-close" @click="closeModal">×</button>
            </header>
            <form class="modal-form" @submit.prevent="submitForm">
              <p v-if="editingService && editingService.managed === false" class="modal-note">
                自动发现的容器不会写入配置，保存后会将其加入列表以便自定义。
              </p>
              <label>
                名称
                <input v-model="form.name" placeholder="例如 Emby" required />
              </label>
              <label>
                描述
                <input v-model="form.description" placeholder="显示在卡片上的描述" />
              </label>
              <label>
                面板地址
                <input
                  v-model="form.access_url"
                  placeholder="https://dashboard.example.com"
                  @blur="deriveIcon"
                  required
                />
                <span class="form-hint">用于点击卡片时跳转，也会自动抓取图标</span>
              </label>
              <label>
                API / 探活地址（可选）
                <input v-model="form.endpoint" placeholder="http://service/status" />
                <span class="form-hint">留空则仅根据 Docker 状态判断在线</span>
              </label>

              <button class="advanced-toggle" type="button" @click="showAdvanced = !showAdvanced">
                {{ showAdvanced ? '隐藏高级选项' : '展开高级选项' }}
              </button>

              <transition name="fade">
                <div v-if="showAdvanced" class="advanced-fields">
                  <label>
                    Docker 容器名称
                    <input v-model="form.container" placeholder="docker 容器名，可选" />
                  </label>
                  <label>
                    标签（逗号分隔）
                    <input v-model="form.tags" placeholder="media,home" />
                  </label>
                  <label>
                    自定义图标 URL
                    <input v-model="form.icon" placeholder="https://..." />
                  </label>
                </div>
              </transition>

              <div class="modal-actions">
                <button type="submit" class="primary-button" :disabled="submitting">
                  {{ submitting ? '保存中...' : '保存' }}
                </button>
                <button type="button" class="action-btn action-btn--ghost" @click="closeModal">取消</button>
              </div>
            </form>
          </div>
        </div>
      </teleport>
    </div>
  </AppShell>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import AppShell from '../components/layout/AppShell.vue'
import DockerServiceCard from '../components/docker/DockerServiceCard.vue'
import { useDockerOverview } from '../composables/useDockerOverview'
import { useDockerServices } from '../composables/useDockerServices'

const {
  data: overview,
  loading: overviewLoading,
  error: overviewError,
  startPolling,
  stopPolling,
  load: loadOverview,
} = useDockerOverview()

const { create, update, getBySlug } = useDockerServices()
const showModal = ref(false)
const submitting = ref(false)
const form = ref(getEmptyForm())
const showAdvanced = ref(false)
const editingService = ref(null)
const editingConfig = ref(null)

const dockerServices = computed(() => {
  if (!overview.value || !Array.isArray(overview.value.services)) return []
  return overview.value.services.slice()
})

const summary = computed(() => overview.value?.summary || null)

const panelSubtitle = computed(() => {
  if (!summary.value) return overviewLoading.value ? '正在刷新 Docker 状态...' : '暂无数据'
  return `总计 ${summary.value.total} 项服务，${summary.value.online} 个在线`
})

const isEditing = computed(() => !!editingService.value)
const hasPersistedConfig = computed(() => !!editingConfig.value)

function getEmptyForm() {
  return {
    name: '',
    description: '',
    access_url: '',
    endpoint: '',
    container: '',
    tags: '',
    icon: '',
  }
}

function startCreate() {
  form.value = getEmptyForm()
  editingService.value = null
  editingConfig.value = null
  showAdvanced.value = false
  showModal.value = true
}

function fillFormFromSource(source) {
  form.value = {
    name: source.name || '',
    description: source.description || '',
    access_url: source.access_url || '',
    endpoint: source.probe?.url || source.endpoint || '',
    container: source.container || '',
    tags: Array.isArray(source.tags) ? source.tags.join(', ') : '',
    icon: source.icon || '',
  }
  showAdvanced.value = Boolean(form.value.container || form.value.tags || form.value.icon)
}

async function startEdit(service) {
  editingService.value = service
  editingConfig.value = null
  fillFormFromSource(service)
  showModal.value = true
  try {
    const cfg = await getBySlug(service.slug)
    if (cfg) {
      editingConfig.value = cfg
      fillFormFromSource(cfg)
    }
  } catch (err) {
    console.error(err)
  }
}

function closeModal() {
  if (submitting.value) return
  editingService.value = null
  editingConfig.value = null
  showModal.value = false
}

function deriveIcon() {
  if (!form.value.access_url) return
  if (form.value.icon) return
  try {
    const url = new URL(form.value.access_url)
    form.value.icon = `https://www.google.com/s2/favicons?sz=64&domain_url=${url.origin}`
  } catch (e) {
    // ignore invalid url
  }
}

async function submitForm() {
  if (submitting.value) return
  submitting.value = true
  const payload = {
    name: form.value.name,
    description: form.value.description || null,
    access_url: form.value.access_url || null,
    icon: form.value.icon || null,
    container: form.value.container || null,
    tags: form.value.tags
      ? form.value.tags.split(',').map((tag) => tag.trim()).filter(Boolean)
      : [],
    probe: {
      url: form.value.endpoint || null,
      method: 'GET',
      timeout: 3,
      expect_status: [],
    },
    require_probe: false,
  }
  try {
    if (hasPersistedConfig.value && editingConfig.value?.slug) {
      await update(editingConfig.value.slug, payload)
    } else {
      await create(payload)
    }
    await loadOverview()
    showModal.value = false
  } catch (err) {
    console.error(err)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  startPolling(5000)
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.docker-page {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.control-panel {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.panel-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.panel-label {
  font-size: 0.85rem;
  margin: 0;
  opacity: 0.7;
}

.panel-subtitle {
  margin: 0.2rem 0 0;
  font-size: 1.05rem;
  font-weight: 600;
}

.panel-actions {
  display: flex;
  gap: 0.45rem;
}

.icon-button {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.6);
  color: #e2e8f0;
  cursor: pointer;
}

.icon-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.metrics-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.5rem;
}

.metric-chip {
  padding: 0.5rem 0.75rem;
  border-radius: 0.9rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(15, 23, 42, 0.55);
  display: flex;
  flex-direction: column;
  font-size: 0.8rem;
}

.metric-chip strong {
  font-size: 1.2rem;
}

.metric-chip--ok {
  border-color: rgba(34, 197, 94, 0.35);
}

.metric-chip--warn {
  border-color: rgba(248, 113, 113, 0.35);
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1rem;
}

.empty-hint {
  text-align: center;
  opacity: 0.6;
}

.primary-button {
  border: 1px solid rgba(59, 130, 246, 0.5);
  background: rgba(37, 99, 235, 0.25);
  color: #bfdbfe;
  padding: 0.35rem 0.9rem;
  border-radius: 999px;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  width: min(520px, 90%);
  background: rgba(13, 19, 33, 0.95);
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 1rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-close {
  background: transparent;
  border: none;
  font-size: 1.3rem;
  color: #e2e8f0;
  cursor: pointer;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.modal-note {
  font-size: 0.78rem;
  padding: 0.4rem 0.6rem;
  border-radius: 0.6rem;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.form-hint {
  font-size: 0.72rem;
  opacity: 0.6;
}

.advanced-toggle {
  align-self: flex-start;
  padding: 0.2rem 0.5rem;
  border: none;
  background: transparent;
  color: #60a5fa;
  font-size: 0.82rem;
  cursor: pointer;
}

.advanced-fields {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.5rem 0 0;
  border-top: 1px solid rgba(148, 163, 184, 0.15);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.modal-form label {
  display: flex;
  flex-direction: column;
  font-size: 0.82rem;
  gap: 0.3rem;
}

.modal-form input {
  padding: 0.35rem 0.6rem;
  border-radius: 0.6rem;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.4);
  color: inherit;
}

.modal-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.action-btn {
  padding: 0.3rem 0.9rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.4);
  color: #e2e8f0;
}

.action-btn--ghost {
  background: transparent;
}
</style>
