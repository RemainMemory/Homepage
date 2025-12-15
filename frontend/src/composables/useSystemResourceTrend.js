import { ref, onMounted, onBeforeUnmount } from 'vue'
import { fetchSystemResourceTrend } from '../api/system'

const DEFAULT_INTERVAL = 5000

export function useSystemResourceTrend(options = {}) {
  const { interval = DEFAULT_INTERVAL } = options

  const points = ref([])
  const loading = ref(false)
  const error = ref(null)

  let timerId = null

  async function load() {
    loading.value = true
    error.value = null
    try {
      const data = await fetchSystemResourceTrend({ limit: options.limit ?? 120 })
      points.value = data?.points ?? []
    } catch (err) {
      error.value = err
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  function schedule() {
    if (interval <= 0) return
    timerId = setInterval(load, interval)
  }

  function start() {
    stop()
    load()
    schedule()
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
    points,
    loading,
    error,
    reload: load,
    start,
    stop,
  }
}

export default { useSystemResourceTrend }
