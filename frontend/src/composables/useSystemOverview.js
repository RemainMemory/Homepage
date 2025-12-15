import { ref, onMounted, onBeforeUnmount } from 'vue'
import {
  fetchSystemSummary,
  fetchSystemProcesses,
  fetchSystemSensors,
  fetchSystemUptime,
} from '../api/system'

const DEFAULT_INTERVAL = 5000

export function useSystemOverview(options = {}) {
  const refreshInterval = options.interval ?? DEFAULT_INTERVAL
  const loading = ref(false)
  const error = ref(null)
  const summary = ref(null)
  const processes = ref(null)
  const sensors = ref(null)
  const uptime = ref(null)

  let timerId = null

  async function load() {
    loading.value = true
    error.value = null
    try {
      const [summaryData, processesData, sensorsData, uptimeData] = await Promise.all([
        fetchSystemSummary(),
        fetchSystemProcesses({ limit: 10 }),
        fetchSystemSensors(),
        fetchSystemUptime(),
      ])
      summary.value = summaryData
      processes.value = processesData
      sensors.value = sensorsData
      uptime.value = uptimeData
    } catch (err) {
      error.value = err
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  function startAutoRefresh() {
    stopAutoRefresh()
    if (refreshInterval > 0) {
      timerId = setInterval(load, refreshInterval)
    }
  }

  function stopAutoRefresh() {
    if (timerId) {
      clearInterval(timerId)
      timerId = null
    }
  }

  load()
  onMounted(startAutoRefresh)
  onBeforeUnmount(stopAutoRefresh)

  return {
    loading,
    error,
    summary,
    processes,
    sensors,
    uptime,
    reload: load,
    startAutoRefresh,
    stopAutoRefresh,
  }
}

export default { useSystemOverview }
