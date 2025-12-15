// src/composables/useHostOverview.js
import { ref } from 'vue'
import { fetchHostOverview } from '../api/host'

export function useHostOverview() {
  const loading = ref(false)      // 首次加载用
  const error = ref(null)
  const data = ref(null)

  let pollTimer = null

  async function load() {
    // 每次都更新，但只在没有数据时才显示“加载中”
    loading.value = true
    error.value = null
    try {
      const res = await fetchHostOverview()
      data.value = res
    } catch (e) {
      console.error(e)
      error.value = e
    } finally {
      loading.value = false
    }
  }

  function startPolling(intervalMs = 5000) {
    // 先立即拉一次
    load()

    // 再定时刷新
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
