<template>
  <section class="card glass external-monitor-card">
    <!-- 顶部：标题 + 概览 pill -->
    <header class="card-header">
      <div class="title-block">
        <div class="title-line">
          <span class="title-icon">🛰️</span>
          <h2>外部服务</h2>
        </div>
        <p class="subtitle">反向代理 / 面板 / 外网服务健康状态</p>
      </div>

      <div class="header-status">
        <div
          v-if="hasSummary"
          class="status-pill"
          :class="statusOk ? 'status-pill--ok' : 'status-pill--warn'"
        >
          <span class="status-dot"></span>
          <span class="status-text">
            {{ monitor.summary.online }}/{{ monitor.summary.total }} 在线
          </span>
        </div>
        <span v-else class="status-text--muted">未配置监控</span>
      </div>
    </header>

    <!-- 有数据时 -->
    <div class="card-body" v-if="hasSummary">
      <!-- 顶部大号数字 -->
      <div class="summary-row">
        <div class="summary-main">
          <div class="summary-label">在线率</div>
          <div class="summary-value">
            {{ onlinePctDisplay }}
            <span class="summary-unit">%</span>
          </div>
        </div>

        <div class="summary-side">
          <div class="summary-side-label">服务数量</div>
          <div class="summary-side-value">
            {{ monitor.summary.online }}
            <span class="summary-side-split">/</span>
            <span class="summary-side-total">{{ monitor.summary.total }}</span>
          </div>
        </div>
      </div>

      <div class="section-divider"></div>

      <!-- 下方两列指标 -->
      <div class="stat-grid">
        <div class="stat-card">
          <div class="stat-label">平均延迟</div>
          <div class="stat-value">
            <template v-if="monitor.summary.avg_latency_ms !== null">
              {{ monitor.summary.avg_latency_ms.toFixed(1) }} ms
            </template>
            <template v-else>-</template>
          </div>
          <div class="stat-hint">以所有监控目标为样本</div>
        </div>

        <div class="stat-card">
          <div class="stat-label">状态摘要</div>
          <div class="stat-value">
            <span v-if="statusOk">整体正常</span>
            <span v-else>存在异常服务</span>
          </div>
          <div class="stat-hint">
            {{ monitor.summary.online }} 个可用 ·
            {{ Math.max(monitor.summary.total - monitor.summary.online, 0) }} 个不可用
          </div>
        </div>
      </div>
    </div>

    <!-- 无数据时 -->
    <div class="card-body" v-else>
      <div class="empty-row">
        <span class="empty-dot"></span>
        <span class="empty-label">监控模块</span>
        <span class="empty-text">未配置或后端不可用</span>
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

const hasSummary = computed(() => {
  return !!props.monitor?.summary && typeof props.monitor.summary.total === 'number'
})

const statusOk = computed(() => {
  if (!hasSummary.value) return false
  const { online, total } = props.monitor.summary
  if (!total || total <= 0) return false
  return online === total
})

const onlinePctDisplay = computed(() => {
  if (!hasSummary.value) return '0.0'
  const { online, total } = props.monitor.summary
  if (!total || total <= 0) return '0.0'
  const pct = (online / total) * 100
  return pct.toFixed(1)
})
</script>

<style scoped>
/* ===== 概览区域 ===== */
.summary-row {
  margin-top: 0.5rem;
  padding: 0.45rem 0.75rem;
  border-radius: 0.8rem;
  background: linear-gradient(
    135deg,
    rgba(15, 23, 42, 0.82),
    rgba(15, 23, 42, 0.72)
  );
  border: 1px solid rgba(148, 163, 184, 0.35);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.summary-main {
  display: flex;
  flex-direction: column;
  gap: 0.12rem;
}

.summary-label {
  font-size: 0.74rem;
  opacity: 0.72;
}

.summary-value {
  font-size: 1.2rem;
  font-weight: 600;
  display: flex;
  align-items: baseline;
  gap: 0.18rem;
}

.summary-unit {
  font-size: 0.74rem;
  opacity: 0.7;
}

.summary-side {
  text-align: right;
  display: flex;
  flex-direction: column;
  gap: 0.08rem;
}

.summary-side-label {
  font-size: 0.72rem;
  opacity: 0.68;
}

.summary-side-value {
  font-size: 0.9rem;
  font-weight: 500;
}

.summary-side-split {
  opacity: 0.6;
  padding: 0 2px;
}

.summary-side-total {
  opacity: 0.8;
}

/* ===== 区块分隔线 ===== */
.section-divider {
  margin-top: 0.6rem;
  border-top: 1px solid rgba(148, 163, 184, 0.24);
}

/* ===== 下方指标网格 ===== */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.55rem;
  margin-top: 0.55rem;
}

.stat-card {
  padding: 0.45rem 0.6rem;
  border-radius: 0.75rem;
  background: rgba(15, 23, 42, 0.72);
  border: 1px solid rgba(30, 64, 175, 0.36);
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.stat-label {
  font-size: 0.72rem;
  opacity: 0.66;
}

.stat-value {
  font-size: 0.9rem;
  font-weight: 500;
}

.stat-hint {
  font-size: 0.7rem;
  opacity: 0.52;
  margin-top: 0.04rem;
}

/* ===== 空状态 ===== */
.empty-row {
  margin-top: 0.1rem;
  padding: 0.45rem 0.7rem;
  border-radius: 0.8rem;
  border: 1px dashed rgba(148, 163, 184, 0.4);
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.8rem;
  opacity: 0.9;
}

.empty-dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.9);
}

.empty-label {
  opacity: 0.7;
}

.empty-text {
  font-weight: 500;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .summary-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .summary-side {
    text-align: left;
  }
}
</style>
