import { ref, onMounted, onBeforeUnmount } from 'vue'
import { fetchNetworkOverview } from '../api/network'

const DEFAULT_INTERVAL = 5000

export function useNetworkOverview(options = {}) {
  const interval = options.interval ?? DEFAULT_INTERVAL
  const loading = ref(false)
  const error = ref(null)
  const overview = ref(null)
  let timerId = null

  async function load() {
    loading.value = true
    error.value = null
    try {
      overview.value = await fetchNetworkOverview()
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
    overview,
    reload: load,
    start,
    stop,
  }
}

export default { useNetworkOverview }
