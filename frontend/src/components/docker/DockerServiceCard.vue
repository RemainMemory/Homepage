<template>
  <article class="docker-service-card" :class="{ 'docker-service-card--down': !service.online }">
    <div class="card-body">
      <div class="service-header">
        <div class="service-icon">{{ iconDisplay }}</div>
        <div class="service-info">
          <div class="service-title">
            {{ service.name }}
            <span v-if="service.state" class="service-state">{{ service.state }}</span>
          </div>
          <p class="service-desc">{{ service.description || service.status_text || '无描述' }}</p>
          <div v-if="service.tags?.length" class="service-tags">
            <span v-for="tag in service.tags" :key="tag">#{{ tag }}</span>
          </div>
        </div>
        <div class="service-status">
          <span class="status-dot" :class="service.online ? 'status-dot--ok' : 'status-dot--down'"></span>
          <span>{{ service.online ? '在线' : '离线' }}</span>
        </div>
      </div>

      <ul class="service-metrics">
        <li>
          <span class="metric-label">延迟</span>
          <span class="metric-value">{{ latencyDisplay }}</span>
        </li>
        <li>
          <span class="metric-label">响应</span>
          <span class="metric-value">{{ service.response_code ?? '--' }}</span>
        </li>
        <li>
          <span class="metric-label">最后探测</span>
          <span class="metric-value">{{ lastCheckedDisplay }}</span>
        </li>
      </ul>
    </div>

    <div class="service-actions">
      <a
        v-if="service.access_url"
        :href="service.access_url"
        class="action-btn"
        target="_blank"
        rel="noreferrer"
      >
        面板
      </a>
      <button
        v-if="service.endpoint"
        class="action-btn"
        @click="$emit('open-api', service.endpoint)"
      >
        API
      </button>
      <button v-if="service.endpoint" class="action-btn action-btn--ghost" @click="$emit('copy', service)">
        复制 API
      </button>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  service: {
    type: Object,
    required: true,
  },
})

defineEmits(['copy', 'open-api'])

const iconDisplay = computed(() => {
  const icon = props.service.icon
  if (!icon) return '🐳'
  if (icon.startsWith('mdi-')) {
    const text = icon.replace('mdi-', '')
    return text ? text[0].toUpperCase() : 'M'
  }
  return icon
})

const latencyDisplay = computed(() => {
  const latency = props.service.latency_ms
  if (latency === null || latency === undefined) return '--'
  if (latency >= 1000) return `${(latency / 1000).toFixed(1)} s`
  return `${latency.toFixed(1)} ms`
})

const lastCheckedDisplay = computed(() => {
  if (!props.service.last_checked) return '--'
  const date = new Date(props.service.last_checked)
  if (Number.isNaN(date.getTime())) return props.service.last_checked
  return date.toLocaleTimeString()
})
</script>

<style scoped>
.docker-service-card {
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 1.1rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  background: rgba(15, 23, 42, 0.6);
}

.docker-service-card--down {
  border-color: rgba(248, 113, 113, 0.4);
  background: rgba(15, 23, 42, 0.45);
}

.card-header {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
}

.service-header {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.service-icon {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  background: rgba(59, 130, 246, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
}

.service-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.18rem;
  min-width: 0;
}

.service-title {
  font-size: 1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.service-state {
  padding: 0.1rem 0.5rem;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.2);
  font-size: 0.7rem;
  text-transform: uppercase;
}

.service-desc {
  margin: 0;
  font-size: 0.8rem;
  opacity: 0.75;
}

.service-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.service-tags span {
  font-size: 0.7rem;
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  background: rgba(94, 234, 212, 0.12);
  color: #a5f3fc;
}

.service-status {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-weight: 600;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #94a3b8;
}

.status-dot--ok {
  background: #22c55e;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.8);
}

.status-dot--down {
  background: #ef4444;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.7);
}

.service-metrics {
  margin: 0.6rem 0 0;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.35rem;
  list-style: none;
  padding: 0;
}

.service-metrics li {
  padding: 0.4rem 0.5rem;
  border-radius: 0.75rem;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.metric-label {
  font-size: 0.72rem;
  opacity: 0.7;
}

.metric-value {
  font-weight: 600;
}

.service-actions {
  margin-top: 0.8rem;
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.35);
  color: #bfdbfe;
  font-size: 0.78rem;
}

.action-btn--ghost {
  background: transparent;
  border-color: rgba(148, 163, 184, 0.4);
  color: #e2e8f0;
}
</style>
