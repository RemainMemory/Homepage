<template>
  <section class="card glass docker-card">
    <header class="card-header">
      <div class="title-block">
        <div class="title-line">
          <span class="title-icon">🐳</span>
          <h2>Docker 服务</h2>
        </div>
        <p class="subtitle">容器运行情况 · 快捷入口</p>
      </div>

      <div class="header-status" v-if="summary">
        <div class="status-pill" :class="summary.online === summary.total ? 'status-pill--ok' : 'status-pill--warn'">
          <span class="status-dot"></span>
          <span class="status-text">
            {{ summary.online }}/{{ summary.total }} 在线
          </span>
        </div>
      </div>
    </header>

    <div class="card-body" v-if="hasServices">
      <div class="summary-grid">
        <div class="summary-item">
          <div class="summary-label">运行中</div>
          <div class="summary-value">{{ summary.running }}</div>
        </div>
        <div class="summary-item">
          <div class="summary-label">在线</div>
          <div class="summary-value">{{ summary.online }}</div>
        </div>
        <div class="summary-item">
          <div class="summary-label">异常</div>
          <div class="summary-value summary-value--warn">{{ summary.unhealthy }}</div>
        </div>
      </div>

      <p v-if="props.docker?.message" class="hint-text">
        {{ props.docker.message }}
      </p>

      <ul class="service-list">
        <li v-for="svc in previewServices" :key="svc.slug" class="service-row">
          <div class="service-main">
            <span class="service-dot" :class="svc.online ? 'service-dot--ok' : 'service-dot--down'"></span>
            <span class="service-icon">{{ iconFor(svc) }}</span>
            <div class="service-texts">
              <div class="service-name">
                {{ svc.name }}
                <span v-if="svc.state" class="service-state">{{ svc.state }}</span>
              </div>
              <div class="service-desc">{{ svc.description || svc.status_text || '无描述' }}</div>
              <div class="service-tags" v-if="svc.tags?.length">
                <span v-for="tag in svc.tags" :key="tag" class="service-tag">#{{ tag }}</span>
              </div>
              <div v-if="svc.stats?.headline" class="service-headline">
                {{ svc.stats.headline }}
              </div>
              <div v-if="svc.stats?.items?.length" class="service-mini-stats">
                <span v-for="item in limitedStats(svc.stats.items)" :key="item.label" class="mini-stat">
                  {{ item.label }}: {{ item.value }}
                </span>
              </div>
            </div>
          </div>
          <div class="service-metrics">
            <span class="metric">{{ formatLatency(svc.latency_ms) }}</span>
            <span class="metric metric--muted" v-if="svc.response_code">HTTP {{ svc.response_code }}</span>
          </div>
          <div class="service-actions">
            <a
              v-if="svc.access_url"
              class="action-btn"
              :href="svc.access_url"
              target="_blank"
              rel="noreferrer"
            >
              快捷接入
            </a>
            <RouterLink class="action-btn action-btn--ghost" to="/docker">详情</RouterLink>
          </div>
        </li>
      </ul>

      <RouterLink class="view-all-link" to="/docker">
        查看全部 Docker 服务 →
      </RouterLink>
    </div>

    <div v-else class="card-body empty-body">
      <p>暂无 Docker 配置或服务不可用。</p>
      <RouterLink to="/docker" class="action-btn action-btn--ghost">管理 Docker 服务</RouterLink>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  docker: {
    type: Object,
    default: null,
  },
})

const hasServices = computed(() => {
  return Array.isArray(props.docker?.services) && props.docker.services.length > 0
})

const summary = computed(() => props.docker?.summary || null)

const previewServices = computed(() => {
  if (!hasServices.value) return []
  return props.docker.services.slice(0, 4)
})

function formatLatency(latency) {
  if (latency === null || latency === undefined) return '--'
  if (latency >= 1000) {
    return `${(latency / 1000).toFixed(1)} s`
  }
  return `${latency.toFixed(1)} ms`
}

function iconFor(service) {
  if (!service?.icon) return '🐳'
  return service.icon
}

function limitedStats(items) {
  if (!Array.isArray(items)) return []
  return items.slice(0, 2)
}
</script>

<style scoped>
.docker-card {
  display: flex;
  flex-direction: column;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.summary-item {
  background: rgba(15, 23, 42, 0.55);
  border-radius: 0.75rem;
  border: 1px solid rgba(148, 163, 184, 0.25);
  padding: 0.5rem 0.75rem;
}

.summary-label {
  font-size: 0.75rem;
  opacity: 0.7;
}

.summary-value {
  font-size: 1.1rem;
  font-weight: 600;
}

.summary-value--warn {
  color: #f97316;
}

.hint-text {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-bottom: 0.4rem;
}

.service-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.service-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.45rem 0.5rem;
  border-radius: 0.9rem;
  border: 1px solid rgba(148, 163, 184, 0.25);
}

.service-main {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  flex: 1 1 40%;
}

.service-icon {
  font-size: 1.25rem;
  line-height: 1;
}

.service-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  background: #94a3b8;
}

.service-dot--ok {
  background: #22c55e;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.8);
}

.service-dot--down {
  background: #ef4444;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.6);
}

.service-texts {
  display: flex;
  flex-direction: column;
}

.service-name {
  font-weight: 600;
}

.service-state {
  margin-left: 0.35rem;
  padding: 0.05rem 0.4rem;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.18);
  font-size: 0.7rem;
  text-transform: uppercase;
  opacity: 0.8;
}

.service-desc {
  font-size: 0.75rem;
  opacity: 0.7;
}

.service-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-top: 0.15rem;
}

.service-tag {
  font-size: 0.7rem;
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.1);
  color: #bfdbfe;
}

.service-headline {
  font-size: 0.78rem;
  color: #fcd34d;
  margin-top: 0.2rem;
}

.service-mini-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  margin-top: 0.2rem;
  font-size: 0.73rem;
  opacity: 0.8;
}

.mini-stat {
  padding: 0.15rem 0.4rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.service-metrics {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 110px;
  font-size: 0.8rem;
  opacity: 0.8;
}

.service-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.25);
  color: #93c5fd;
  font-size: 0.78rem;
  text-decoration: none;
}

.metric--muted {
  opacity: 0.6;
}

.action-btn--ghost {
  background: transparent;
  border-color: rgba(148, 163, 184, 0.3);
  color: #e2e8f0;
}

.view-all-link {
  margin-top: 0.75rem;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.85rem;
  color: #93c5fd;
}

.empty-body {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
</style>
