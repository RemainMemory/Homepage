<template>
  <section class="card glass network-card">
    <!-- 顶部：标题 + 状态 -->
    <header class="card-header">
      <div class="title-block">
        <div class="title-line">
          <span class="title-icon">🌐</span>
          <h2>网络状态</h2>
        </div>
        <div class="subtitle">
          <span class="if-name">{{ primaryName || '未识别出口网卡' }}</span>
          <span v-if="primaryIpv4" class="if-ip">
            · {{ primaryIpv4 }}
          </span>
        </div>
      </div>

      <div class="header-status">
        <div
          class="status-pill"
          :class="internetOk ? 'status-pill--ok' : 'status-pill--bad'"
        >
          <span class="status-dot"></span>
          <span class="status-text">{{ internetOk ? '已联网' : '未联网' }}</span>
        </div>
      </div>
    </header>

    <div class="card-body" v-if="network">
      <!-- 速率 -->
      <div class="net-hero net-hero--stack">
        <div class="hero-item hero-item--down">
          <div class="hero-label">
            <span class="hero-dot hero-dot--down"></span>
            下行
          </div>
          <div class="hero-value">
            {{ formatMbps(network.summary?.total_rx_mbps) }}
            <span class="hero-unit">Mbps</span>
          </div>
        </div>

        <div class="hero-item hero-item--up">
          <div class="hero-label">
            <span class="hero-dot hero-dot--up"></span>
            上行
          </div>
          <div class="hero-value">
            {{ formatMbps(network.summary?.total_tx_mbps) }}
            <span class="hero-unit">Mbps</span>
          </div>
        </div>
      </div>

      <!-- 延迟 + 公网 IP -->
      <div class="net-meta">
        <div class="meta-cell">
          <div class="meta-label">外网延迟</div>
          <div class="meta-value">
            {{ formatMs(network.summary?.internet_latency_ms) }}
          </div>
          <div class="meta-hint">到 1.1.1.1:443</div>
        </div>

        <div class="meta-cell">
          <div class="meta-label">网关延迟</div>
          <div class="meta-value">
            {{ formatMs(network.summary?.gateway_latency_ms) }}
          </div>
          <div class="meta-hint meta-hint--ellipsis">
            {{ routesGateway || '默认网关' }}
          </div>
        </div>

        <div class="meta-cell meta-cell--wide">
          <div class="meta-label">公网 IP</div>
          <div v-if="network.summary?.public_ip" class="meta-value meta-value--mono">
            {{ network.summary.public_ip }}
          </div>
          <div v-else class="meta-value meta-value--muted">未获取</div>
          <div class="meta-hint">当前出口地址</div>
        </div>
      </div>
    </div>

    <div class="card-body" v-else>
      <div class="empty-row">
        <span class="empty-label">网络状态</span>
        <span class="empty-dot"></span>
        <span class="empty-text">暂无数据</span>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  network: {
    type: Object,
    required: true,
  },
})

const internetOk = computed(() => !!props.network?.summary?.internet_ok)

const primaryName = computed(() => props.network?.summary?.primary_interface || null)

const primaryIpv4 = computed(() => {
  const name = primaryName.value
  if (!name || !props.network?.interfaces) return null
  const iface = props.network.interfaces.find((i) => i.name === name)
  return iface?.ipv4 || null
})

const routesGateway = computed(() => props.network?.routes?.default_gateway || '')

const formatMbps = (v) => {
  if (v === null || v === undefined) return '0.00'
  const num = Number(v)
  if (!Number.isFinite(num)) return '0.00'
  return num.toFixed(2)
}

const formatMs = (v) => {
  if (v === null || v === undefined) return '-'
  const num = Number(v)
  if (!Number.isFinite(num)) return '-'
  return `${num.toFixed(1)} ms`
}

</script>

<style scoped>
.network-card .subtitle {
  display: flex;
  align-items: center;
  gap: 0.15rem;
}

.if-name {
  letter-spacing: 0.03em;
}

.if-ip {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
    'Liberation Mono', 'Courier New', monospace;
  opacity: 0.7;
}

/* ===== Hero row ===== */
.net-hero {
  margin-top: 0.35rem;
  padding: 0.35rem 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(200px, 1fr));
  max-width: 640px;
  margin-left: auto;
  margin-right: auto;
  gap: 0.75rem;
}

.net-hero--stack {
  grid-template-columns: minmax(0, 400px);
  justify-content: center;
  gap: 0.55rem;
}

.hero-item {
  padding: 0.65rem 0.8rem;
  border-radius: 1rem;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.08),
    0 15px 30px rgba(1, 8, 19, 0.6);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.hero-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  align-items: flex-start;
}

.hero-chart {
  width: 140px;
  height: 48px;
  border-radius: 0.8rem;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(15, 23, 42, 0.3);
  padding: 0.2rem 0.35rem;
}

.hero-chart svg {
  width: 100%;
  height: 100%;
}

.hero-chart--down {
  border-color: rgba(56, 189, 248, 0.35);
  background: radial-gradient(circle at 15% 30%, rgba(56, 189, 248, 0.18), rgba(15, 23, 42, 0.3));
}

.hero-chart--up {
  border-color: rgba(52, 211, 153, 0.35);
  background: radial-gradient(circle at 85% 30%, rgba(52, 211, 153, 0.18), rgba(15, 23, 42, 0.3));
}

.hero-item--down {
  background: radial-gradient(circle at 25% 20%, rgba(56, 189, 248, 0.28), rgba(15, 23, 42, 0.58));
  border: 1px solid rgba(56, 189, 248, 0.3);
  text-align: left;
  align-items: flex-start;
}

.hero-item--up {
  background: radial-gradient(circle at 75% 20%, rgba(52, 211, 153, 0.25), rgba(15, 23, 42, 0.58));
  border: 1px solid rgba(52, 211, 153, 0.3);
  text-align: right;
  align-items: flex-end;
}

.hero-label {
  font-size: 0.8rem;
  opacity: 0.78;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}

.hero-item--down .hero-label {
  justify-content: flex-start;
}

.hero-item--up .hero-label {
  justify-content: flex-end;
}

.hero-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  box-shadow: 0 0 8px currentColor;
}

.hero-dot--down {
  background: #38bdf8;
}

.hero-dot--up {
  background: #34d399;
}

.hero-value {
  font-size: 1.4rem;
  font-weight: 600;
  display: flex;
  align-items: baseline;
  gap: 0.28rem;
  letter-spacing: 0.01em;
}

.hero-unit {
  font-size: 0.82rem;
  opacity: 0.75;
}

/* ===== Meta grid ===== */
.net-meta {
  margin-top: 0.4rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.55rem;
}

.meta-cell {
  padding: 0.45rem 0.6rem;
  border-radius: 0.85rem;
  background: rgba(15, 23, 42, 0.45);
  border: 1px solid rgba(148, 163, 184, 0.2);
  display: flex;
  flex-direction: column;
  gap: 0.16rem;
  min-width: 0;
}

.meta-cell--wide {
  grid-column: span 2;
}

.meta-label {
  font-size: 0.74rem;
  opacity: 0.68;
  letter-spacing: 0.01em;
}

.meta-value {
  font-size: 0.98rem;
  font-weight: 600;
  letter-spacing: 0.01em;
}

.meta-value--muted {
  opacity: 0.55;
  font-size: 0.92rem;
}

.meta-value--mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
    'Liberation Mono', 'Courier New', monospace;
  letter-spacing: 0.04em;
}

.meta-hint {
  font-size: 0.68rem;
  opacity: 0.5;
  margin-top: 0.02rem;
}

.meta-hint--ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ===== 空状态 ===== */
.empty-row {
  margin-top: 0.1rem;
  padding: 0.4rem 0.55rem;
  border-radius: 0.7rem;
  border: 1px dashed rgba(148, 163, 184, 0.4);
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8rem;
  opacity: 0.85;
}

.empty-label {
  opacity: 0.7;
}

.empty-dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.9);
}

.empty-text {
  font-weight: 500;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .network-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .status-pill {
    align-self: flex-start;
  }

  .meta-cell--wide {
    grid-column: span 1;
  }

}
</style>
