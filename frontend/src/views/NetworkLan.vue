<template>
  <AppShell>
    <div class="dashboard network-lan">
      <header class="section-header">
        <div>
          <h1>LAN 在线设备</h1>
          <p>基于 ARP 表统计最近通信的局域网设备。</p>
        </div>
        <div class="section-header__actions">
          <button class="refresh-button" :disabled="loading" @click="reload">
            <span class="refresh-button__icon" aria-hidden="true">⟳</span>
            <span>{{ loading ? '刷新中...' : '刷新列表' }}</span>
          </button>
        </div>
      </header>

      <div v-if="loading && !devices.length" class="dash-status">扫描中...</div>
      <div v-else-if="error" class="dash-status dash-status--error">加载失败：{{ error.message }}</div>

      <section class="panel" v-else>
        <header class="panel-header">
          <div>
            <h2>最近发现的设备</h2>
            <p>共 {{ devices.length }} 台 · {{ collectedLabel }}</p>
          </div>
        </header>

        <div class="table-wrap">
          <table class="lan-table" v-if="devices.length">
            <thead>
              <tr>
                <th>IP</th>
                <th>MAC</th>
                <th>厂商</th>
                <th>主机名</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="dev in devices" :key="dev.ip + dev.mac">
                <td>{{ dev.ip }}</td>
                <td>
                  {{ dev.mac || '--' }}
                </td>
                <td>{{ dev.vendor || '--' }}</td>
                <td>{{ dev.hostname || '--' }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else class="dash-status">暂无设备</div>
        </div>
      </section>
    </div>
  </AppShell>
</template>

<script setup>
import { computed } from 'vue'
import AppShell from '../components/layout/AppShell.vue'
import { useLanDevices } from '../composables/useLanDevices'

const { devices, collectedAt, loading, error, reload } = useLanDevices()

const collectedLabel = computed(() => {
  if (!collectedAt.value) return '时间未知'
  const date = new Date(collectedAt.value)
  return `采集于 ${date.toLocaleTimeString()}`
})
</script>

<style scoped>
.network-lan {
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

.table-wrap {
  overflow-x: auto;
}

.lan-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.lan-table th,
.lan-table td {
  padding: 0.45rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
  text-align: left;
}

.meta {
  font-size: 0.75rem;
  opacity: 0.65;
}
</style>
