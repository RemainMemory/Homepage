<template>
  <AppShell>
    <div class="dashboard system-monitor">
      <header class="section-header">
        <div>
          <h1>系统监控</h1>
          <p>更全面的 CPU / 内存 / 进程 / 传感器信息</p>
        </div>
        <div class="section-header__actions">
          <button class="refresh-button" @click="reload" :disabled="loading">
            <span class="refresh-button__icon" aria-hidden="true">⟳</span>
            <span>{{ loading ? '刷新中...' : '刷新数据' }}</span>
          </button>
        </div>
      </header>

      <div v-if="loading && !summary" class="dash-status">加载中...</div>
      <div v-else-if="error" class="dash-status dash-status--error">
        加载失败：{{ error.message }}
      </div>

      <div v-else-if="summary" class="system-content">
        <div class="summary-row">
          <SystemSummaryCard :system="summary" :uptime="uptime" :show-details="true" />
          <section class="panel trend-panel">
          <header class="panel-header">
            <div>
              <h2>资源趋势</h2>
              <p>CPU / 内存 / 网络的最近采样（自动每 5 秒更新）</p>
            </div>
            <div class="panel-header-actions">
              <button
                class="refresh-button refresh-button--compact"
                @click="reloadTrend"
                :disabled="trendLoading"
              >
                <span class="refresh-button__icon" aria-hidden="true">⟳</span>
                <span>{{ trendLoading ? '更新中...' : '刷新趋势' }}</span>
              </button>
            </div>
          </header>

          <div v-if="trendError" class="dash-status dash-status--error">
            趋势加载失败：{{ trendError.message }}
          </div>

          <div v-else>
            <div v-if="!trendPoints.length" class="dash-status">暂无趋势数据</div>
            <div v-else class="trend-chart-wrap">
              <svg class="trend-chart" viewBox="0 0 100 100" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="cpuGradient" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stop-color="#60a5fa" stop-opacity="0.9" />
                    <stop offset="100%" stop-color="#38bdf8" stop-opacity="0.5" />
                  </linearGradient>
                  <linearGradient id="memGradient" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stop-color="#f472b6" stop-opacity="0.85" />
                    <stop offset="100%" stop-color="#f97316" stop-opacity="0.5" />
                  </linearGradient>
                  <linearGradient id="netGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="rgba(52, 211, 153, 0.5)" />
                    <stop offset="100%" stop-color="rgba(16, 185, 129, 0.05)" />
                  </linearGradient>
                </defs>

                <path :d="chartSeries.netRx" class="trend-area trend-area--rx" />
                <path :d="chartSeries.netTx" class="trend-area trend-area--tx" />
                <path :d="chartSeries.cpu" class="trend-line trend-line--cpu" />
                <path :d="chartSeries.memory" class="trend-line trend-line--mem" />
                <path :d="chartSeries.netRxLine" class="trend-line trend-line--rx" />
                <path :d="chartSeries.netTxLine" class="trend-line trend-line--tx" />
              </svg>

              <div class="trend-legend">
                <span><i class="dot dot--cpu"></i>CPU</span>
                <span><i class="dot dot--mem"></i>内存</span>
                <span><i class="dot dot--rx"></i>下载</span>
                <span><i class="dot dot--tx"></i>上传</span>
                <span class="trend-scale">网络刻度：{{ netScaleLabel }}</span>
              </div>

              <div class="trend-stats" v-if="latestTrend">
                <div class="stat-pill">
                  <span>CPU</span>
                  <strong>{{ formatPercent(latestTrend.cpu_pct) }}%</strong>
                </div>
                <div class="stat-pill">
                  <span>内存</span>
                  <strong>{{ formatPercent(latestTrend.memory_pct) }}%</strong>
                </div>
                <div class="stat-pill">
                  <span>下载</span>
                  <strong>{{ formatMbps(latestTrend.net_rx_mbps) }} Mbps</strong>
                </div>
                <div class="stat-pill">
                  <span>上传</span>
                  <strong>{{ formatMbps(latestTrend.net_tx_mbps) }} Mbps</strong>
                </div>
              </div>
            </div>
          </div>
          </section>
        </div>

        <section class="panel">
          <header class="panel-header">
            <div>
              <h2>Top 进程</h2>
              <p>实时展示 CPU / 内存占用最高的进程</p>
            </div>
          </header>
          <div class="process-columns">
            <div>
              <h3>按 CPU</h3>
              <table class="process-table">
                <thead>
                  <tr>
                    <th>进程</th>
                    <th>用户</th>
                    <th>CPU %</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in topCpu" :key="`cpu-${item.pid}`">
                    <td>
                      <div class="proc-name">{{ item.name }}</div>
                      <div class="proc-meta">PID {{ item.pid }}</div>
                    </td>
                    <td>{{ item.username || '--' }}</td>
                    <td>
                      {{ item.cpu_pct?.toFixed(1) ?? '--' }}
                      <span class="proc-unit">%</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div>
              <h3>按内存</h3>
              <table class="process-table">
                <thead>
                  <tr>
                    <th>进程</th>
                    <th>用户</th>
                    <th>内存 MB</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in topMem" :key="`mem-${item.pid}`">
                    <td>
                      <div class="proc-name">{{ item.name }}</div>
                      <div class="proc-meta">PID {{ item.pid }}</div>
                    </td>
                    <td>{{ item.username || '--' }}</td>
                    <td>
                      {{ item.memory_mb?.toFixed(1) ?? '--' }}
                      <span class="proc-unit">MB</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <section class="panel">
          <header class="panel-header">
            <div>
              <h2>传感器</h2>
              <p>温度、风扇、笔记本电池状态</p>
            </div>
          </header>

          <div class="sensor-grid">
            <SensorCard
              v-for="temp in topTemps"
              :key="temp.label"
              :label="temp.label"
              :value="temp.current"
              unit="°C"
            />
          </div>

          <div class="sensor-extras">
            <div class="fan-list" v-if="fans.length">
              <h3>风扇</h3>
              <ul>
                <li v-for="fan in fans" :key="fan.name">
                  <span>{{ fan.name }}</span>
                  <strong>{{ fan.rpm }} RPM</strong>
                </li>
              </ul>
            </div>
            <div class="battery-card" v-if="battery">
              <h3>电池</h3>
              <p v-if="battery.present">
                {{ battery.percent ?? '--' }}% ·
                {{ battery.power_plugged ? '已接入电源' : '电池供电' }}
              </p>
              <p v-else>未检测到电池</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  </AppShell>
</template>

<script setup>
import { computed, defineComponent } from 'vue'
import AppShell from '../components/layout/AppShell.vue'
import SystemSummaryCard from '../components/dashboard/SystemSummaryCard.vue'
import { useSystemOverview } from '../composables/useSystemOverview'
import { useSystemResourceTrend } from '../composables/useSystemResourceTrend'

const { summary, processes, sensors, uptime, loading, error, reload } = useSystemOverview()
const {
  points: trendPoints,
  loading: trendLoading,
  error: trendError,
  reload: reloadTrend,
} = useSystemResourceTrend({ interval: 5000, limit: 120 })

const topCpu = computed(() => processes.value?.top_by_cpu ?? [])
const topMem = computed(() => processes.value?.top_by_memory ?? [])
const topTemps = computed(() => sensors.value?.temperatures?.slice(0, 6) ?? [])
const fans = computed(() => sensors.value?.fans ?? [])
const battery = computed(() => sensors.value?.battery ?? null)
const latestTrend = computed(() => {
  const list = trendPoints.value ?? []
  return list.length ? list[list.length - 1] : null
})

const netScaleLabel = computed(() => {
  const maxNet = Math.max(
    1,
    ...((trendPoints.value ?? []).map((pt) =>
      Math.max(pt.net_rx_mbps ?? 0, pt.net_tx_mbps ?? 0)
    ) ?? [1])
  )
  return `${maxNet.toFixed(1)} Mbps`
})

const chartSeries = computed(() => {
  const pts = trendPoints.value ?? []
  if (!pts.length) {
    return {
      cpu: '',
      memory: '',
      netRx: '',
      netTx: '',
      netRxLine: '',
      netTxLine: '',
    }
  }
  const cpu = buildPath(pts, 'cpu_pct', 100)
  const memory = buildPath(pts, 'memory_pct', 100)
  const netMax = Math.max(
    1,
    ...pts.map((pt) => Math.max(pt.net_rx_mbps ?? 0, pt.net_tx_mbps ?? 0))
  )
  const netRxLine = buildPath(pts, 'net_rx_mbps', netMax)
  const netTxLine = buildPath(pts, 'net_tx_mbps', netMax)
  return {
    cpu,
    memory,
    netRx: makeAreaPath(pts, 'net_rx_mbps', netMax),
    netTx: makeAreaPath(pts, 'net_tx_mbps', netMax),
    netRxLine,
    netTxLine,
  }
})

function buildPath(points, key, maxValue) {
  const filtered = points.filter((pt) => Number.isFinite(pt[key]))
  if (!points.length || !filtered.length) return ''
  const denom = points.length - 1 || 1
  return points
    .map((pt, idx) => {
      const value = Number(pt[key] ?? 0)
      const clamped = Math.max(0, Math.min(maxValue, value))
      const x = (idx / denom) * 100
      const y = 100 - (clamped / (maxValue || 1)) * 100
      const cmd = idx === 0 ? 'M' : 'L'
      return `${cmd}${x.toFixed(2)},${y.toFixed(2)}`
    })
    .join(' ')
}

function makeAreaPath(points, key, maxValue) {
  if (!points.length) return ''
  const denom = points.length - 1 || 1
  const coords = points.map((pt, idx) => {
    const value = Number(pt[key] ?? 0)
    const clamped = Math.max(0, Math.min(maxValue, value))
    const x = (idx / denom) * 100
    const y = 100 - (clamped / (maxValue || 1)) * 100
    return { x: Number(x.toFixed(2)), y: Number(y.toFixed(2)) }
  })
  const start = coords[0]
  const end = coords[coords.length - 1]

  const topPath = coords
    .map((c, idx) => {
      const cmd = idx === 0 ? 'M' : 'L'
      return `${cmd}${c.x},${c.y}`
    })
    .join(' ')

  return `${topPath} L${end.x},100 L${start.x},100 Z`
}

function formatPercent(value) {
  if (value == null) return '--'
  return Number(value).toFixed(1)
}

function formatMbps(value) {
  if (value == null) return '--'
  if (value >= 10) return Number(value).toFixed(1)
  return Number(value).toFixed(2)
}

const SensorCard = defineComponent({
  name: 'SensorCard',
  props: {
    label: String,
    value: Number,
    unit: String,
  },
  template: `
    <div class="sensor-card">
      <div class="sensor-value">
        {{ value?.toFixed(1) ?? '--' }} <span>{{ unit }}</span>
      </div>
      <div class="sensor-label">{{ label }}</div>
    </div>
  `,
})
</script>

<style scoped>
.system-monitor {
  gap: 20px;
}

.system-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.summary-row {
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
  gap: 20px;
  align-items: stretch;
}

@media (max-width: 1100px) {
  .summary-row {
    grid-template-columns: 1fr;
  }
}

.trend-panel {
  min-height: 100%;
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
  font-size: 1.05rem;
}

.panel-header p {
  margin: 4px 0 0;
  opacity: 0.7;
  font-size: 0.85rem;
}

.panel-header-actions {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.trend-chart-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.trend-chart {
  width: 100%;
  height: 150px;
  border-radius: 0.85rem;
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.trend-line {
  fill: none;
  stroke-width: 1.4;
  stroke-linecap: round;
  stroke-linejoin: round;
  opacity: 0.9;
}

.trend-area {
  fill: url(#netGradient);
  opacity: 0.25;
}

.trend-area--tx {
  opacity: 0.15;
}

.trend-line--cpu {
  stroke: url(#cpuGradient);
}

.trend-line--mem {
  stroke: url(#memGradient);
}

.trend-line--rx {
  stroke: rgba(52, 211, 153, 0.85);
}

.trend-line--tx {
  stroke: rgba(16, 185, 129, 0.85);
}

.trend-legend {
  display: flex;
  gap: 1.2rem;
  flex-wrap: wrap;
  font-size: 0.8rem;
  opacity: 0.8;
}

.trend-scale {
  margin-left: auto;
  font-variant-numeric: tabular-nums;
}

.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 999px;
  margin-right: 4px;
}

.dot--cpu {
  background: #60a5fa;
}

.dot--mem {
  background: #f472b6;
}

.dot--rx {
  background: #34d399;
}

.dot--tx {
  background: #10b981;
}

.trend-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.75rem;
}

.stat-pill {
  border-radius: 0.85rem;
  border: 1px solid rgba(148, 163, 184, 0.15);
  padding: 0.65rem 0.75rem;
  background: rgba(15, 23, 42, 0.35);
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  font-size: 0.85rem;
}

.stat-pill strong {
  font-size: 1.1rem;
  font-variant-numeric: tabular-nums;
}

.process-columns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.process-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.process-table th,
.process-table td {
  padding: 0.45rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
  text-align: left;
}

.proc-name {
  font-weight: 600;
}

.proc-meta {
  font-size: 0.75rem;
  opacity: 0.6;
}

.proc-unit {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-left: 2px;
}

.sensor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.75rem;
}

.sensor-card {
  padding: 0.75rem;
  border-radius: 0.85rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(15, 23, 42, 0.4);
}

.sensor-value {
  font-size: 1.2rem;
  font-weight: 600;
}

.sensor-value span {
  font-size: 0.8rem;
  opacity: 0.7;
}

.sensor-label {
  margin-top: 0.2rem;
  font-size: 0.85rem;
  opacity: 0.75;
}

.sensor-extras {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.fan-list ul {
  list-style: none;
  padding: 0;
  margin: 0.5rem 0 0;
}

.fan-list li {
  display: flex;
  justify-content: space-between;
  padding: 0.35rem 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.15);
}

.battery-card {
  min-width: 200px;
  padding: 0.75rem;
  border-radius: 0.85rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(15, 23, 42, 0.35);
}
</style>
