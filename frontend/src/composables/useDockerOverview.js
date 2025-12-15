import { ref } from 'vue'
import { fetchDockerOverview } from '../api/docker'

export function useDockerOverview() {
  const loading = ref(false)
  const error = ref(null)
  const data = ref(null)
  let pollTimer = null

  async function load() {
    try {
      loading.value = true
      error.value = null
      data.value = await fetchDockerOverview()
    } catch (err) {
      console.error(err)
      error.value = err
    } finally {
      loading.value = false
    }
  }

  function startPolling(intervalMs = 5000) {
    load()
    stopPolling()
    pollTimer = setInterval(load, intervalMs)
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  return {
    loading,
    error,
    data,
    load,
    startPolling,
    stopPolling,
  }
}
