import { ref, onMounted, onBeforeUnmount } from 'vue'
import { fetchLanDevices } from '../api/network'

const DEFAULT_INTERVAL = 15000

export function useLanDevices(options = {}) {
  const interval = options.interval ?? DEFAULT_INTERVAL
  const loading = ref(false)
  const error = ref(null)
  const devices = ref([])
  const collectedAt = ref(null)
  let timerId = null

  async function load() {
    loading.value = true
    error.value = null
    try {
      const data = await fetchLanDevices()
      devices.value = data?.devices ?? []
      collectedAt.value = data?.collected_at || data?.collectedAt || null
    } catch (err) {
      error.value = err
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  function start() {
    stop()
    load()
    if (interval > 0) {
      timerId = setInterval(load, interval)
    }
  }

  function stop() {
    if (timerId) {
      clearInterval(timerId)
      timerId = null
    }
  }

  onMounted(start)
  onBeforeUnmount(stop)

  return {
    loading,
    error,
    devices,
    collectedAt,
    reload: load,
    start,
    stop,
  }
}

export default { useLanDevices }
