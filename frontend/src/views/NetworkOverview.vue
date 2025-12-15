<template>
  <AppShell>
    <div class="dashboard network-page">
      <header class="section-header">
        <div>
          <h1>网络监控</h1>
          <p>出口速率、网卡状态、连通性与路由表一目了然。</p>
        </div>
        <div class="section-header__actions">
          <button class="refresh-button" @click="reload" :disabled="loading">
            <span class="refresh-button__icon" aria-hidden="true">⟳</span>
            <span>{{ loading ? '刷新中...' : '刷新数据' }}</span>
          </button>
        </div>
      </header>

      <div v-if="loading && !overview" class="dash-status">加载网络信息...</div>
      <div v-else-if="error" class="dash-status dash-status--error">加载失败：{{ error.message }}</div>

      <div v-else-if="overview" class="network-content">
        <section class="panel summary-panel">
          <header class="panel-header">
            <div>
              <h2>总体概览</h2>
              <p>主出口速率、公网 IP 与连通性状态。</p>
            </div>
          </header>

          <div class="summary-grid">
            <article class="summary-card">
              <div class="summary-label">出口速率</div>
              <div class="summary-value">{{ formatMbps(summary.wan_rx_mbps) }} ↓ / {{ formatMbps(summary.wan_tx_mbps) }} ↑</div>
              <p class="summary-sub">总速率：{{ formatMbps(summary.total_rx_mbps) }} / {{ formatMbps(summary.total_tx_mbps) }} Mbps</p>
            </article>
            <article class="summary-card">
              <div class="summary-label">公网 IP</div>
              <div class="summary-value">{{ summary.public_ip || '--' }}</div>
              <p class="summary-sub">默认接口：{{ summary.primary_interface || '--' }}</p>
            </article>
            <article class="summary-card status-card" :class="{ 'status-card--ok': connectivity.internet_ok, 'status-card--bad': !connectivity.internet_ok }">
              <div class="summary-label">外网连通性</div>
              <div class="summary-value">
                {{ connectivity.internet_ok ? '已联网' : '异常' }}
              </div>
              <p class="summary-sub">
                延迟 {{ formatLatency(connectivity.internet_latency_ms || summary.internet_latency_ms) }}
              </p>
            </article>
            <article class="summary-card">
              <div class="summary-label">默认网关延迟</div>
              <div class="summary-value">{{ formatLatency(summary.gateway_latency_ms) }}</div>
              <p class="summary-sub">
                默认网关：
                {{ routes.default_gateway || '--' }}
              </p>
            </article>
          </div>
        </section>

        <section class="panel">
          <header class="panel-header">
            <div>
              <h2>连通性详情</h2>
              <p>快速查看外网、网关、DNS 状态。</p>
            </div>
          </header>
          <div class="connectivity-row">
            <div class="connectivity-card" v-for="item in connectivityCards" :key="item.label" :class="{ 'is-ok': item.ok, 'is-bad': item.ok === false }">
              <div class="conn-label">{{ item.label }}</div>
              <div class="conn-value">{{ item.value }}</div>
              <p class="conn-sub">{{ item.sub }}</p>
            </div>
          </div>
        </section>

        <section class="panel">
          <header class="panel-header">
            <div>
              <h2>网卡 / 接口</h2>
              <p>各接口速率、IP、流量及利用率。</p>
            </div>
          </header>
          <div class="interface-table-wrap">
            <table class="interface-table">
              <thead>
                <tr>
                  <th>接口</th>
                  <th>状态</th>
                  <th>IPv4 / IPv6</th>
                  <th>速率</th>
                  <th>利用率</th>
                  <th>下行</th>
                  <th>上行</th>
                  <th>错误</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="iface in interfaces" :key="iface.name">
                  <td>
                    <div class="iface-name">
                      <strong>{{ iface.display_name || iface.name }}</strong>
                      <span v-if="iface.role" class="iface-role">{{ iface.role }}</span>
                      <span v-if="iface.is_primary" class="iface-pill">主</span>
                    </div>
                    <div class="iface-meta">{{ iface.type || '接口' }} · MAC {{ iface.mac || '--' }}</div>
                  </td>
                  <td>
                    <span :class="['state-dot', iface.state === 'up' ? 'state-dot--up' : 'state-dot--down']"></span>
                    {{ iface.state === 'up' ? 'UP' : 'DOWN' }}
                  </td>
                  <td>
                    <div>{{ iface.ipv4 || '--' }}</div>
                    <div class="iface-meta">{{ iface.ipv6 || '' }}</div>
                  </td>
                  <td>{{ iface.speed_mbps ? `${iface.speed_mbps} Mbps` : '--' }}</td>
                  <td>
                    <div class="util-bar">
                      <div class="util-bar__fill" :style="{ width: utilizationWidth(iface.utilization_pct) }"></div>
                    </div>
                    <div class="iface-meta">{{ formatPercent(iface.utilization_pct) }}</div>
                  </td>
                  <td>
                    <div>{{ formatMbps(iface.rx?.rate_mbps) }}</div>
                    <div class="iface-meta">{{ prettyBytes(iface.rx?.bytes) }}</div>
                  </td>
                  <td>
                    <div>{{ formatMbps(iface.tx?.rate_mbps) }}</div>
                    <div class="iface-meta">{{ prettyBytes(iface.tx?.bytes) }}</div>
                  </td>
                  <td>
                    <span class="error-chip" v-if="iface.rx?.errors || iface.tx?.errors">
                      ERR {{ iface.rx?.errors ?? 0 }}/{{ iface.tx?.errors ?? 0 }}
                    </span>
                    <span class="error-chip warn" v-if="iface.rx?.dropped || iface.tx?.dropped">
                      DROP {{ iface.rx?.dropped ?? 0 }}/{{ iface.tx?.dropped ?? 0 }}
                    </span>
                    <span v-if="!hasError(iface)" class="iface-meta">0</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="panel">
          <header class="panel-header">
            <div>
              <h2>路由表</h2>
              <p>默认网关、出口 IP 以及主要路由。</p>
            </div>
          </header>
          <div class="routes-info">
            <div>默认网关：<strong>{{ routes.default_gateway || '--' }}</strong></div>
            <div>默认接口：<strong>{{ routes.default_interface || '--' }}</strong></div>
            <div>公网 IP：<strong>{{ routes.public_ip || summary.public_ip || '--' }}</strong></div>
          </div>
          <div class="interface-table-wrap">
            <table class="route-table" v-if="routes.routes?.length">
              <thead>
                <tr>
                  <th>目标</th>
                  <th>网关</th>
                  <th>接口</th>
                  <th>Metric</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="route in routes.routes" :key="route.dst + route.interface">
                  <td>{{ route.dst }}</td>
                  <td>{{ route.gateway || '-' }}</td>
                  <td>{{ route.interface || '-' }}</td>
                  <td>{{ route.metric ?? '-' }}</td>
                </tr>
              </tbody>
            </table>
            <div v-else class="dash-status">暂无路由信息</div>
          </div>
        </section>
      </div>
    </div>
  </AppShell>
</template>

<script setup>
import { computed } from 'vue'
import AppShell from '../components/layout/AppShell.vue'
import { useNetworkOverview } from '../composables/useNetworkOverview'

const { overview, loading, error, reload } = useNetworkOverview({ interval: 7000 })

const summary = computed(() => overview.value?.summary ?? {})
const connectivity = computed(() => overview.value?.connectivity ?? {})
const routes = computed(() => overview.value?.routes ?? {})
const interfaces = computed(() => overview.value?.interfaces ?? [])

const connectivityCards = computed(() => {
  const cards = [
    {
      label: '外网',
      ok: connectivity.value.internet_ok,
      value: connectivity.value.internet_ok ? '可用' : '异常',
      sub: connectivity.value.tested_internet_target || '1.1.1.1:443',
    },
    {
      label: '默认网关',
      ok: connectivity.value.gateway_ok,
      value: formatLatency(connectivity.value.gateway_latency_ms),
      sub: 'Gateway',
    },
    {
      label: 'DNS',
      ok: connectivity.value.dns_ok,
      value: connectivity.value.dns_ok ? formatLatency(connectivity.value.dns_latency_ms) : '失败',
      sub: connectivity.value.tested_dns_target || '系统 DNS',
    },
  ]

  cards.push({
    label: '抖动',
    ok: connectivity.value.jitter_ms != null,
    value: connectivity.value.jitter_ms != null ? formatLatency(connectivity.value.jitter_ms) : '--',
    sub: 'Jitter',
  })
  cards.push({
    label: '丢包',
    ok: connectivity.value.packet_loss_pct != null,
    value: formatPercent(connectivity.value.packet_loss_pct),
    sub: 'Packet Loss',
  })

  return cards
})

function formatMbps(value) {
  if (value == null) return '--'
  const n = Number(value)
  if (!Number.isFinite(n)) return '--'
  if (n >= 100) return n.toFixed(0)
  if (n >= 10) return n.toFixed(1)
  return n.toFixed(2)
}

function formatLatency(value) {
  if (value == null) return '--'
  const n = Number(value)
  if (!Number.isFinite(n)) return '--'
  return `${n.toFixed(1)} ms`
}

function prettyBytes(bytes) {
  if (bytes == null) return '--'
  let n = Number(bytes)
  if (!Number.isFinite(n)) return '--'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let idx = 0
  while (n >= 1024 && idx < units.length - 1) {
    n /= 1024
    idx += 1
  }
  return `${n.toFixed(idx === 0 ? 0 : 1)} ${units[idx]}`
}

function formatPercent(value) {
  if (value == null) return '--'
  const n = Number(value)
  if (!Number.isFinite(n)) return '--'
  return `${n.toFixed(1)}%`
}

function utilizationWidth(value) {
  if (value == null || !Number.isFinite(Number(value))) return '0%'
  return `${Math.max(0, Math.min(100, Number(value))).toFixed(1)}%`
}

function hasError(iface) {
  return Boolean(iface.rx?.errors || iface.tx?.errors || iface.rx?.dropped || iface.tx?.dropped)
}
</script>

<style scoped>
.network-page {
  gap: 20px;
}

.network-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 1rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.panel-header h2 {
  margin: 0;
}

.panel-header p {
  margin: 4px 0 0;
  opacity: 0.75;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.summary-card {
  border-radius: 1rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(15, 23, 42, 0.4);
  padding: 0.85rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.summary-label {
  font-size: 0.78rem;
  opacity: 0.75;
  letter-spacing: 0.04em;
}

.summary-value {
  font-size: 1.2rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.summary-sub {
  margin: 0;
  font-size: 0.85rem;
  opacity: 0.7;
}

.status-card {
  border-color: rgba(34, 197, 94, 0.3);
}

.status-card--bad {
  border-color: rgba(248, 113, 113, 0.3);
}

.connectivity-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
}

.connectivity-card {
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 0.9rem;
  padding: 0.8rem;
  background: rgba(15, 23, 42, 0.4);
}

.connectivity-card.is-ok {
  border-color: rgba(34, 197, 94, 0.3);
}

.connectivity-card.is-bad {
  border-color: rgba(248, 113, 113, 0.3);
}

.conn-label {
  font-size: 0.85rem;
  opacity: 0.75;
}

.conn-value {
  font-size: 1.1rem;
  font-weight: 600;
}

.conn-sub {
  margin: 0.2rem 0 0;
  font-size: 0.85rem;
  opacity: 0.7;
}

.interface-table-wrap {
  overflow-x: auto;
}

.interface-table,
.route-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.interface-table th,
.interface-table td,
.route-table th,
.route-table td {
  padding: 0.45rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
  text-align: left;
}

.iface-name {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.iface-role {
  font-size: 0.7rem;
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.3);
}

.iface-pill {
  font-size: 0.65rem;
  border-radius: 999px;
  background: rgba(56, 189, 248, 0.15);
  color: #bae6fd;
  padding: 0.05rem 0.35rem;
}

.iface-meta {
  font-size: 0.75rem;
  opacity: 0.6;
}

.util-bar {
  width: 100%;
  height: 6px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.25);
  overflow: hidden;
  margin-bottom: 2px;
}

.util-bar__fill {
  height: 100%;
  background: linear-gradient(90deg, rgba(14, 165, 233, 0.3), rgba(14, 165, 233, 0.95));
}

.error-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.2rem;
  padding: 0.1rem 0.35rem;
  border-radius: 0.7rem;
  border: 1px solid rgba(248, 113, 113, 0.5);
  color: #fecaca;
  font-size: 0.72rem;
  margin-right: 0.25rem;
}

.error-chip.warn {
  border-color: rgba(251, 191, 36, 0.5);
  color: #fde68a;
}

.state-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  display: inline-block;
  margin-right: 4px;
}

.state-dot--up {
  background: #22c55e;
}

.state-dot--down {
  background: #ef4444;
}

.routes-info {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  font-size: 0.9rem;
  opacity: 0.85;
}
</style>
