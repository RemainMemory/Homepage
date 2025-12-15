import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import SystemOverview from '../views/SystemOverview.vue'
import SystemDisks from '../views/SystemDisks.vue'
import SystemEvents from '../views/SystemEvents.vue'
import NetworkOverview from '../views/NetworkOverview.vue'
import NetworkLan from '../views/NetworkLan.vue'
import NetworkSpeed from '../views/NetworkSpeed.vue'
import MonitorTargets from '../views/MonitorTargets.vue'
import DockerOverview from '../views/DockerOverview.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
  },
  {
    path: '/system',
    name: 'SystemOverview',
    component: SystemOverview,
  },
  {
    path: '/system/disks',
    name: 'SystemDisks',
    component: SystemDisks,
  },
  {
    path: '/system/events',
    name: 'SystemEvents',
    component: SystemEvents,
  },
  {
    path: '/network',
    name: 'NetworkOverview',
    component: NetworkOverview,
  },
  {
    path: '/network/lan',
    name: 'NetworkLan',
    component: NetworkLan,
  },
  {
    path: '/network/speed',
    name: 'NetworkSpeed',
    component: NetworkSpeed,
  },
  {
    path: '/monitor/targets',
    name: 'MonitorTargets',
    component: MonitorTargets,
  },
  {
    path: '/docker',
    name: 'DockerOverview',
    component: DockerOverview,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
