<template>
  <nav class="side-nav glass">
    <div class="side-nav__logo">
      <span class="logo-dot"></span>
      <span class="logo-text">Skyler Dashboard</span>
    </div>

    <div class="side-nav__sections">
      <div v-for="group in navGroups" :key="group.title" class="side-nav__section">
        <div class="side-nav__section-title">{{ group.title }}</div>
        <ul class="side-nav__menu">
          <li v-for="link in group.links" :key="link.name" :class="{ active: route.name === link.name }">
            <RouterLink :to="link.to">{{ link.label }}</RouterLink>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const navGroups = computed(() => [
  {
    title: '仪表盘',
    links: [{ name: 'Dashboard', label: '总览', to: '/' }],
  },
  {
    title: '系统监控',
    links: [
      { name: 'SystemOverview', label: '系统摘要', to: '/system' },
      { name: 'SystemDisks', label: '磁盘 / 文件', to: '/system/disks' },
      { name: 'SystemEvents', label: '事件 / 登录', to: '/system/events' },
    ],
  },
  {
    title: '网络监控',
    links: [
      { name: 'NetworkOverview', label: '网络概览', to: '/network' },
      { name: 'NetworkLan', label: 'LAN 设备', to: '/network/lan' },
      { name: 'NetworkSpeed', label: '网络测速', to: '/network/speed' },
    ],
  },
  {
    title: '服务监控',
    links: [
      { name: 'DockerOverview', label: 'Docker 服务', to: '/docker' },
      { name: 'MonitorTargets', label: '监控 Targets', to: '/monitor/targets' },
    ],
  },
])
</script>
