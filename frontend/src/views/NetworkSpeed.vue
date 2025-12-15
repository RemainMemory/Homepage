<template>
  <AppShell>
    <div class="dashboard network-speed">
      <header class="section-header">
        <div>
          <h1>网络测速</h1>
          <p>调用 speedtest-cli，获取当前下载 / 上传带宽与延迟。</p>
        </div>
        <div class="section-header__actions">
          <button class="refresh-button" :disabled="running" @click="run">
            <span class="refresh-button__icon" aria-hidden="true">⟳</span>
            <span>{{ running ? '测速中...' : '开始测速' }}</span>
          </button>
        </div>
      </header>

      <div v-if="error" class="dash-status dash-status--error">测速失败：{{ error.message }}</div>

      <section class="panel">
        <header class="panel-header">
          <div>
            <h2>最新结果</h2>
            <p>测速完成后会自动更新。</p>
          </div>
        </header>
        <div v-if="running && !result" class="dash-status">测速进行中...</div>
        <div v-else-if="result" class="speed-grid">
          <div class="speed-card">
            <div class="speed-label">Ping</div>
            <div class="speed-value">{{ formatLatency(result.ping_ms) }}</div>
          </div>
          <div class="speed-card">
            <div class="speed-label">下载</div>
            <div class="speed-value">{{ formatMbps(result.download_mbps) }} Mbps</div>
          </div>
          <div class="speed-card">
            <div class="speed-label">上传</div>
            <div class="speed-value">{{ formatMbps(result.upload_mbps) }} Mbps</div>
          </div>
          <div class="speed-card">
            <div class="speed-label">状态</div>
            <div class="speed-value">{{ result.ok ? '成功' : '失败' }}</div>
            <p class="speed-sub">{{ result.message || '' }}</p>
          </div>
        </div>
        <div v-else class="dash-status">尚未测速，点击上方按钮开始。</div>
      </section>

      <section class="panel" v-if="result?.raw_output">
        <header class="panel-header">
          <div>
            <h2>原始输出</h2>
          </div>
        </header>
        <pre class="raw-output">{{ result.raw_output }}</pre>
      </section>
    </div>
  </AppShell>
</template>

<script setup>
import AppShell from '../components/layout/AppShell.vue'
import { useSpeedtest } from '../composables/useSpeedtest'

const { run, running, result, error } = useSpeedtest()

function formatLatency(value) {
  if (value == null) return '--'
  return `${value.toFixed(1)} ms`
}

function formatMbps(value) {
  if (value == null) return '--'
  const n = Number(value)
  if (!Number.isFinite(n)) return '--'
  if (n >= 100) return n.toFixed(0)
  if (n >= 10) return n.toFixed(1)
  return n.toFixed(2)
}
</script>

<style scoped>
.network-speed {
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

.speed-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.speed-card {
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 0.9rem;
  padding: 0.85rem;
  background: rgba(15, 23, 42, 0.4);
}

.speed-label {
  font-size: 0.8rem;
  opacity: 0.75;
}

.speed-value {
  font-size: 1.4rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.speed-sub {
  margin: 0.2rem 0 0;
  font-size: 0.85rem;
  opacity: 0.7;
}

.raw-output {
  margin: 0;
  white-space: pre-wrap;
  font-size: 0.85rem;
  opacity: 0.8;
}
</style>
