<template>
  <AppShell>
    <div class="dashboard docker-page">
      <header class="section-header">
        <div>
          <h1>Docker 服务</h1>
          <p>快速查看容器在线情况，并直接进入面板或 API。</p>
        </div>
        <button class="refresh-button refresh-button--compact" @click="loadOverview" :disabled="overviewLoading">
          <span class="refresh-button__icon">⟳</span>
          <span>{{ overviewLoading ? '刷新中' : '刷新状态' }}</span>
        </button>
      </header>

      <div v-if="overviewError" class="dash-status dash-status--error">
        获取 Docker 状态失败：{{ overviewError.message }}
      </div>

      <section v-if="overview" class="card glass docker-summary-card">
        <header class="card-header">
          <h2>概览</h2>
          <span class="status-pill" :class="overview.summary.online === overview.summary.total ? 'status-pill--ok' : 'status-pill--warn'">
            <span class="status-dot"></span>
            <span class="status-text">{{ overview.summary.online }}/{{ overview.summary.total }} 在线</span>
          </span>
        </header>
        <div class="card-body summary-grid">
          <div class="summary-item">
            <div class="summary-label">运行中</div>
            <div class="summary-value">{{ overview.summary.running }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">在线</div>
            <div class="summary-value">{{ overview.summary.online }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">异常</div>
            <div class="summary-value summary-value--warn">{{ overview.summary.unhealthy }}</div>
          </div>
          <div class="summary-item summary-item--wide" v-if="overview.message">
            <div class="summary-label">提示</div>
            <div class="summary-value">{{ overview.message }}</div>
          </div>
        </div>
      </section>

      <section class="card glass">
        <header class="card-header">
          <h2>服务卡片</h2>
          <span class="tag tag--green">{{ dockerServices.length }} 项</span>
        </header>
        <div class="card-body">
          <div v-if="dockerServices.length" class="services-grid">
            <DockerServiceCard
              v-for="svc in dockerServices"
              :key="svc.slug"
              :service="svc"
              @copy="copyEndpoint"
              @open-api="openApi"
            />
          </div>
          <p v-else class="empty-hint">暂无 Docker 配置或服务不可用。</p>
        </div>
      </section>
    </div>
  </AppShell>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import AppShell from '../components/layout/AppShell.vue'
import DockerServiceCard from '../components/docker/DockerServiceCard.vue'
import { useDockerOverview } from '../composables/useDockerOverview'

const {
  data: overview,
  loading: overviewLoading,
  error: overviewError,
  startPolling,
  stopPolling,
  load: loadOverview,
} = useDockerOverview()

const dockerServices = computed(() => {
  if (!overview.value || !Array.isArray(overview.value.services)) return []
  return [...overview.value.services].sort((a, b) => {
    if (a.online !== b.online) return a.online ? -1 : 1
    const la = a.latency_ms ?? Number.MAX_VALUE
    const lb = b.latency_ms ?? Number.MAX_VALUE
    return la - lb
  })
})

function copyEndpoint(service) {
  if (!service) return
  const text = service.endpoint || service.access_url
  if (!text) return
  navigator.clipboard?.writeText(text).catch(() => {})
}

function openApi(endpoint) {
  if (!endpoint) return
  window.open(endpoint, '_blank', 'noopener')
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
  gap: 1rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.6rem;
}

.summary-item {
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 0.9rem;
  padding: 0.5rem 0.75rem;
}

.summary-item--wide {
  grid-column: 1 / -1;
}

.summary-label {
  font-size: 0.78rem;
  opacity: 0.7;
}

.summary-value {
  font-size: 1.2rem;
  font-weight: 600;
}

.summary-value--warn {
  color: #fb923c;
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
</style>
