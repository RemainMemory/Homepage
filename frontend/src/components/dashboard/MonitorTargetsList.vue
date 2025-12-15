<template>
  <section class="card glass">
    <header class="card-header">
      <h2>外部服务详情</h2>
      <span class="tag tag--green">Targets</span>
    </header>

    <div class="card-body" v-if="monitor && monitor.targets && monitor.targets.length">
      <div
        v-for="item in sortedTargets"
        :key="item.name"
        class="target-row"
      >
        <div class="target-main">
          <div class="target-name">
            <span
              class="status-dot"
              :class="item.status === 'online' ? 'status-dot--ok' : 'status-dot--down'"
            ></span>
            <span>{{ item.name }}</span>
          </div>
          <div class="target-meta">
            <span class="target-type">
              {{ item.type.toUpperCase() }}
            </span>
            <span v-if="item.url" class="target-url">
              {{ item.url }}
            </span>
            <span v-else-if="item.host" class="target-url">
              {{ item.host }}:{{ item.port }}
            </span>
          </div>
        </div>
        <div class="target-metrics">
          <span class="latency" v-if="item.latency_ms !== null">
            {{ item.latency_ms.toFixed(1) }} ms
          </span>
          <span class="latency" v-else>-</span>
          <span class="code" v-if="item.code">
            {{ item.code }}
          </span>
        </div>
      </div>
    </div>

    <div class="card-body" v-else>
      <div class="metric-row">
        <span>状态</span>
        <strong>当前未配置监控目标</strong>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  monitor: {
    type: Object,
    required: false,
    default: null,
  },
})

const sortedTargets = computed(() => {
  if (!props.monitor || !Array.isArray(props.monitor.targets)) return []
  // 在线优先，其次按延迟升序
  return [...props.monitor.targets].sort((a, b) => {
    if (a.status !== b.status) {
      return a.status === 'online' ? -1 : 1
    }
    const la = a.latency_ms ?? Number.MAX_VALUE
    const lb = b.latency_ms ?? Number.MAX_VALUE
    return la - lb
  })
})
</script>

<style scoped>
.target-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
}

.target-row:last-child {
  border-bottom: none;
}

.target-main {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.target-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #9ca3af;
}

.status-dot--ok {
  background: #22c55e;
  box-shadow: 0 0 6px rgba(34, 197, 94, 0.8);
}

.status-dot--down {
  background: #ef4444;
  box-shadow: 0 0 6px rgba(248, 113, 113, 0.8);
}

.target-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 11px;
  color: #9ca3af;
}

.target-type {
  padding: 1px 6px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.2);
}

.target-url {
  max-width: 220px;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.target-metrics {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  font-size: 12px;
}

.latency {
  min-width: 72px;
  text-align: right;
}

.code {
  font-size: 11px;
  color: #9ca3af;
}
</style>
