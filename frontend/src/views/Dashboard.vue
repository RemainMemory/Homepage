<template>
  <AppShell>
    <div class="dashboard">
      <!-- 只有在“还没有数据且正在加载”时，才显示加载占位 -->
      <div v-if="!overview && loading" class="dash-status">
        加载中...
      </div>

      <div v-else-if="error" class="dash-status dash-status--error">
        加载失败：{{ error.message }}
      </div>

      <!-- 有 overview 就直接渲染卡片，轮询时界面不会闪回去“加载中” -->
      <div v-else-if="overview" class="dash-grid">
        <!-- 顶部三张概要卡 -->
        <section class="grid-row">
          <SystemSummaryCard :system="overview.system" :uptime="overview.uptime" :show-details="false" />
          <NetworkCard :network="overview.network" />
          <MonitorSummaryCard :monitor="overview.monitor" />
        </section>

        <!-- 第二行：Docker & 外部服务详情 -->
        <section class="grid-row grid-row--two">
          <DockerServicesCard :docker="overview.docker" />
          <MonitorTargetsList :monitor="overview.monitor" />
        </section>
      </div>

      <div v-else class="dash-status">
        暂无数据
      </div>
    </div>
  </AppShell>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import AppShell from '../components/layout/AppShell.vue'
import SystemSummaryCard from '../components/dashboard/SystemSummaryCard.vue'
import NetworkCard from '../components/dashboard/NetworkCard.vue'
import MonitorSummaryCard from '../components/dashboard/MonitorSummaryCard.vue'
import MonitorTargetsList from '../components/dashboard/MonitorTargetsList.vue'
import DockerServicesCard from '../components/dashboard/DockerServicesCard.vue'
import { useHostOverview } from '../composables/useHostOverview'

const { loading, error, data, startPolling, stopPolling } = useHostOverview()
const overview = data

onMounted(() => {
  // 开启轮询，比如每 5 秒刷新一次
  startPolling(2000)
})

onUnmounted(() => {
  // 离开页面时关闭定时器
  stopPolling()
})
</script>
