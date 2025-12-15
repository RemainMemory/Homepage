<template>
  <section class="card glass docker-card">
    <header class="card-header">
      <div class="title-block">
        <div class="title-line">
          <span class="title-icon">🐳</span>
          <h2>Docker 服务</h2>
        </div>
        <p class="subtitle">总体运行概览</p>
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

    <div class="card-body" v-if="summary">
      <div class="summary-big">
        <div class="summary-total">
          <span class="summary-total__label">监控服务</span>
          <span class="summary-total__value">{{ summary.total }}</span>
        </div>
        <div class="summary-progress">
          <div class="summary-progress__track">
            <div class="summary-progress__bar" :style="{ width: onlinePercent + '%' }"></div>
          </div>
          <span class="summary-progress__hint">
            {{ summary.online }}/{{ summary.total }} 在线
          </span>
        </div>
      </div>

      <div class="pill-row">
        <div class="pill">
          <span>运行中</span>
          <strong>{{ summary.running }}</strong>
        </div>
        <div class="pill pill--ok">
          <span>在线</span>
          <strong>{{ summary.online }}</strong>
        </div>
        <div class="pill pill--warn">
          <span>异常</span>
          <strong>{{ summary.unhealthy }}</strong>
        </div>
      </div>

      <p v-if="props.docker?.message" class="hint-text">
        {{ props.docker.message }}
      </p>

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

const summary = computed(() => props.docker?.summary || null)

const onlinePercent = computed(() => {
  if (!summary.value || summary.value.total === 0) return 0
  return Math.round((summary.value.online / summary.value.total) * 100)
})
</script>

<style scoped>
.docker-card {
  display: flex;
  flex-direction: column;
}

.hint-text {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-bottom: 0.4rem;
}

.view-all-link {
  margin-top: 0.75rem;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  color: #93c5fd;
  font-size: 0.85rem;
}

.empty-body {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  text-align: center;
}

.summary-big {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.9rem;
}

.summary-total__label {
  font-size: 0.78rem;
  opacity: 0.75;
}

.summary-total__value {
  display: block;
  font-size: 2.5rem;
  font-weight: 700;
  line-height: 1.1;
}

.summary-progress {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.summary-progress__track {
  width: 100%;
  height: 8px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.2);
  overflow: hidden;
}

.summary-progress__bar {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #60a5fa, #34d399);
}

.summary-progress__hint {
  font-size: 0.78rem;
  opacity: 0.75;
  text-align: right;
}

.pill-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.6rem;
}

.pill {
  border-radius: 1rem;
  padding: 0.5rem 0.8rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(15, 23, 42, 0.6);
  display: flex;
  flex-direction: column;
  font-size: 0.78rem;
  gap: 0.25rem;
}

.pill strong {
  font-size: 1.1rem;
}

.pill--ok {
  border-color: rgba(34, 197, 94, 0.35);
}

.pill--warn {
  border-color: rgba(249, 115, 22, 0.35);
}
</style>
