<template>
  <section class="card glass system-ring-card">
    <!-- Header -->
    <header class="card-header">
      <div class="title-block">
        <div class="title-line">
          <span class="title-icon">💻</span>
          <h2>系统概览</h2>
        </div>
        <p class="subtitle">CPU · 内存 · 主盘 · 负载</p>
      </div>

      <div class="header-status">
        <div class="uptime-text" v-if="uptime">
          <span class="uptime-label">已运行</span>
          <span class="uptime-value">
            {{ uptime.uptime_human || uptime.uptimeHuman || '-' }}
          </span>
        </div>
      </div>
    </header>

    <!-- 有数据 -->
    <div class="card-body" v-if="system && uptime">
      <!-- 三个压力环 -->
      <div class="ring-row">
        <!-- CPU -->
        <div class="ring-block">
          <div class="ring">
            <div class="ring-track"></div>
            <div class="ring-progress" :style="cpuProgressStyle"></div>
            <div class="ring-inner">
              <span class="ring-value">{{ cpuPercentDisplay }}</span>
              <span class="ring-unit">%</span>
            </div>
          </div>
          <div class="ring-label">CPU</div>
          <div class="ring-sub">当前使用率</div>
        </div>

        <!-- 内存 -->
        <div class="ring-block">
          <div class="ring">
            <div class="ring-track"></div>
            <div class="ring-progress" :style="memProgressStyle"></div>
            <div class="ring-inner">
              <span class="ring-value">{{ memPercentDisplay }}</span>
              <span class="ring-unit">%</span>
            </div>
          </div>
          <div class="ring-label">内存</div>
          <div class="ring-sub">物理占用</div>
        </div>

        <!-- 主盘 -->
        <div class="ring-block">
          <div class="ring">
            <div class="ring-track"></div>
            <div class="ring-progress" :style="diskProgressStyle"></div>
            <div class="ring-inner">
              <span class="ring-value">{{ diskPercentDisplay }}</span>
              <span class="ring-unit">%</span>
            </div>
          </div>
          <div class="ring-label">主盘</div>
          <div class="ring-sub">系统卷使用率</div>
        </div>
      </div>

      <!-- 整体负载色条 -->
      <div class="health-row">
        <div class="health-info">
          <span class="health-label">整体负载</span>
          <span class="health-score">{{ healthScoreDisplay }} 分</span>
        </div>
        <div class="health-bar">
          <div
            class="health-bar-fill"
            :style="{ width: healthBarWidth, background: healthBarColor }"
          ></div>
        </div>
      </div>

      <div v-if="showDetails" class="details-grid">
        <div class="detail-block">
          <div class="detail-title">CPU 详情</div>
          <ul>
            <li v-for="item in cpuDetails" :key="item.label">
              <span class="detail-label">{{ item.label }}</span>
              <span class="detail-value">{{ item.value }}</span>
            </li>
          </ul>
        </div>
        <div class="detail-block">
          <div class="detail-title">内存 / Swap</div>
          <ul>
            <li v-for="item in memoryDetails" :key="item.label">
              <span class="detail-label">{{ item.label }}</span>
              <span class="detail-value">{{ item.value }}</span>
            </li>
          </ul>
        </div>
        <div class="detail-block">
          <div class="detail-title">主盘详情</div>
          <ul>
            <li v-for="item in diskDetails" :key="item.label">
              <span class="detail-label">{{ item.label }}</span>
              <span class="detail-value">{{ item.value }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 无数据 -->
    <div class="card-body" v-else>
      <div class="empty-line">
        <span class="empty-dot"></span>
        <span class="empty-text">暂时没有系统数据</span>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  system: {
    type: Object,
    required: true,
  },
  uptime: {
    type: Object,
    required: true,
  },
  showDetails: {
    type: Boolean,
    default: false,
  },
})

const clampPercent = (v) => {
  const num = Number(v ?? 0)
  if (!Number.isFinite(num)) return 0
  return Math.min(Math.max(num, 0), 100)
}

const formatNumber = (value, digits = 1) => {
  if (value == null || Number.isNaN(Number(value))) return '--'
  return Number(value).toFixed(digits)
}

const formatPercentText = (value, digits = 1) => {
  if (value == null || Number.isNaN(Number(value))) return '--'
  return `${Number(value).toFixed(digits)}%`
}

const formatGb = (value) => {
  if (value == null || Number.isNaN(Number(value))) return '--'
  return `${Number(value).toFixed(1)} GB`
}

// 兼容 usagePct / usage_pct
const rawCpu = computed(() => {
  const cpu = props.system?.cpu || {}
  return cpu.usagePct ?? cpu.usage_pct ?? 0
})

const rawMem = computed(() => {
  const mem = props.system?.memory || {}
  return mem.usagePct ?? mem.usage_pct ?? 0
})

const rawDisk = computed(() => {
  const disk = props.system?.disk || {}
  return disk.usagePct ?? disk.usage_pct ?? 0
})

const cpuPercent = computed(() => clampPercent(rawCpu.value))
const memPercent = computed(() => clampPercent(rawMem.value))
const diskPercent = computed(() => clampPercent(rawDisk.value))

const cpuPercentDisplay = computed(() => cpuPercent.value.toFixed(1))
const memPercentDisplay = computed(() => memPercent.value.toFixed(1))
const diskPercentDisplay = computed(() => diskPercent.value.toFixed(1))

// 生成压力环进度样式：整圈是渐变，用 --progress-angle 裁掉未完成部分
const makeRingProgressStyle = (percent) => {
  const p = clampPercent(percent)
  const angle = (p / 100) * 360
  return {
    '--progress-angle': `${angle}deg`,
  }
}

const cpuProgressStyle = computed(() => makeRingProgressStyle(cpuPercent.value))
const memProgressStyle = computed(() => makeRingProgressStyle(memPercent.value))
const diskProgressStyle = computed(() => makeRingProgressStyle(diskPercent.value))

// 整体「健康分」= 100 - 平均占用
const healthScore = computed(() => {
  const avg = (cpuPercent.value + memPercent.value + diskPercent.value) / 3
  const score = 100 - avg
  return clampPercent(score)
})

const healthScoreDisplay = computed(() => healthScore.value.toFixed(0))
const healthBarWidth = computed(() => `${healthScore.value}%`)

const healthBarColor = computed(() => {
  const s = healthScore.value
  if (s > 70) {
    return 'linear-gradient(90deg, rgba(22, 163, 74, 0.5), rgba(22, 163, 74, 0.95))'
  }
  if (s > 40) {
    return 'linear-gradient(90deg, rgba(245, 158, 11, 0.5), rgba(245, 158, 11, 0.95))'
  }
  return 'linear-gradient(90deg, rgba(239, 68, 68, 0.5), rgba(239, 68, 68, 0.95))'
})

const cpuInfo = computed(() => props.system?.cpu || {})
const memoryInfo = computed(() => props.system?.memory || {})
const diskInfo = computed(() => props.system?.disk || {})

const cpuDetails = computed(() => {
  if (!props.showDetails) return []
  const cpu = cpuInfo.value
  const loadSeries = [cpu.load1, cpu.load5, cpu.load15].map((v) => formatNumber(v, 2))
  return [
    { label: '1 / 5 / 15 分钟负载', value: loadSeries.join(' / ') },
    { label: '逻辑核心', value: cpu.cores ?? '--' },
    {
      label: '用户态 / 内核态',
      value: `${formatPercentText(cpu.userPct)} / ${formatPercentText(cpu.systemPct)}`,
    },
    {
      label: '空闲 / IO 等待',
      value: `${formatPercentText(cpu.idlePct)} / ${formatPercentText(cpu.iowaitPct)}`,
    },
  ]
})

const memoryDetails = computed(() => {
  if (!props.showDetails) return []
  const memory = memoryInfo.value
  return [
    {
      label: '总计 / 已用',
      value: `${formatGb(memory.totalGb)} / ${formatGb(memory.usedGb)}`,
    },
    {
      label: '可用 / 缓存',
      value: `${formatGb(memory.availableGb)} / ${formatGb(memory.cachedGb)}`,
    },
    {
      label: 'Swap 已用',
      value: `${formatGb(memory.swapUsedGb)} / ${formatGb(memory.swapTotalGb)}`,
    },
    { label: 'Swap 使用率', value: formatPercentText(memory.swapUsagePct) },
  ]
})

const diskDetails = computed(() => {
  if (!props.showDetails) return []
  const disk = diskInfo.value
  return [
    { label: '设备 / 类型', value: `${disk.device || '--'} · ${disk.fsType || '--'}` },
    { label: '挂载点', value: disk.mount || '--' },
    {
      label: '容量 / 已用',
      value: `${formatGb(disk.totalGb)} / ${formatGb(disk.usedGb)}`,
    },
    { label: '剩余空间', value: formatGb(disk.freeGb) },
  ]
})
</script>

<style scoped>
/* uptime 区域：和状态 pill 的文字高度对齐 */
.uptime-text {
  font-size: 0.78rem;              /* 与 status-pill 文本一致 */
  line-height: 1;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  opacity: 0.82;
  white-space: nowrap;
  transform: translateY(-0.5px);   /* 让基线和「已联网」对得更齐 */
}

.uptime-label {
  letter-spacing: 0.06em;
}

.uptime-value {
  font-variant-numeric: tabular-nums;
}

/* ===== 压力环行 ===== */
.ring-row {
  margin-top: 0.35rem;
  padding: 0.4rem 0.2rem 0.2rem;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  background: radial-gradient(circle at 50% 0%, rgba(148, 163, 184, 0.1), transparent 65%);
  border-radius: 0.9rem;
}

.ring-block {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.45rem;
  text-align: center;
}

.ring {
  position: relative;
  width: 78px;
  aspect-ratio: 1 / 1;
}

.ring::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(148, 163, 184, 0.25), transparent 60%);
  filter: blur(12px);
  opacity: 0.35;
}

/* 灰色轨道：细、低饱和度 */
.ring-track {
  position: absolute;
  inset: 0;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.92);
  -webkit-mask: radial-gradient(farthest-side, transparent 62%, #000 63%);
  mask: radial-gradient(farthest-side, transparent 62%, #000 63%);
  box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.08);
}

/* 彩色压力环 */
.ring-progress {
  position: absolute;
  inset: 0;
  border-radius: 999px;
  background:
    conic-gradient(
      from -90deg,
      #0ea5e9 0deg,
      #38bdf8 110deg,
      #34d399 180deg,
      #f5d020 260deg,
      #f97316 320deg,
      #f43f5e 360deg
    );
  -webkit-mask:
    radial-gradient(farthest-side, transparent 62%, #fff 63%),
    conic-gradient(
      from -90deg,
      #fff 0deg,
      #fff var(--progress-angle, 0deg),
      transparent var(--progress-angle, 0deg),
      transparent 360deg
    );
  mask:
    radial-gradient(farthest-side, transparent 62%, #fff 63%),
    conic-gradient(
      from -90deg,
      #fff 0deg,
      #fff var(--progress-angle, 0deg),
      transparent var(--progress-angle, 0deg),
      transparent 360deg
    );
  -webkit-mask-composite: source-in;
  mask-composite: intersect;
}

/* 内部小圆：显示数值 */
.ring-inner {
  position: absolute;
  inset: 15px;
  border-radius: 999px;
  background: radial-gradient(circle at 30% 25%, rgba(255, 255, 255, 0.12), rgba(15, 23, 42, 0.9));
  box-shadow:
    inset 0 0 12px rgba(0, 0, 0, 0.55),
    0 12px 25px rgba(2, 8, 23, 0.75);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-variant-numeric: tabular-nums;
}

.ring-value {
  font-size: 1rem;
  font-weight: 600;
  color: #f8fafc;
}

.ring-unit {
  font-size: 0.65rem;
  opacity: 0.78;
}

.ring-label {
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.ring-sub {
  font-size: 0.7rem;
  opacity: 0.55;
}

/* ===== 整体负载条 ===== */
.health-row {
  margin-top: 0.8rem;
  padding: 0.55rem 0.65rem;
  border-radius: 0.85rem;
  background: rgba(15, 23, 42, 0.72);
  border: 1px solid rgba(148, 163, 184, 0.25);
  box-shadow: inset 0 1px 4px rgba(0, 0, 0, 0.35);
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.health-info {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
}

.health-label {
  font-size: 0.78rem;
  opacity: 0.78;
}

.health-score {
  font-size: 0.9rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.health-bar {
  width: 100%;
  height: 6px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.2);
  overflow: hidden;
}

.health-bar-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.35s ease-out;
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35);
}


/* ===== 无数据 ===== */
.empty-line {
  margin-top: 0.2rem;
  font-size: 0.8rem;
  opacity: 0.75;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
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

.details-grid {
  margin-top: 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.75rem;
}

.detail-block {
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 0.85rem;
  padding: 0.65rem 0.8rem;
  background: rgba(15, 23, 42, 0.35);
}

.detail-title {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.7;
  margin-bottom: 0.35rem;
}

.detail-block ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.detail-label {
  font-size: 0.78rem;
  opacity: 0.65;
}

.detail-value {
  font-size: 0.95rem;
  font-variant-numeric: tabular-nums;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .system-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .uptime-text {
    margin-top: 0.1rem;
  }

  .ring-row {
    justify-content: space-between;
    gap: 0.7rem;
  }

  .ring {
    width: 64px;
  }
}
</style>
