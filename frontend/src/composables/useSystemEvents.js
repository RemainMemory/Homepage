import { ref, onMounted, onBeforeUnmount } from 'vue'
import {
  fetchSystemEvents,
  fetchSystemSchedule,
  fetchSystemLoginHistory,
} from '../api/system'

const DEFAULT_INTERVAL = 15000

export function useSystemEvents(options = {}) {
  const {
    eventLimit = 150,
    loginLimit = 50,
    interval = DEFAULT_INTERVAL,
  } = options

  const loading = ref(false)
  const error = ref(null)
  const events = ref([])
  const schedule = ref([])
  const logins = ref([])

  let timerId = null

  async function load() {
    loading.value = true
    error.value = null
    try {
      const [eventsData, scheduleData, loginData] = await Promise.all([
        fetchSystemEvents({ limit: eventLimit }),
        fetchSystemSchedule(),
        fetchSystemLoginHistory({ limit: loginLimit }),
      ])
      events.value = eventsData?.items ?? []
      schedule.value = scheduleData?.entries ?? []
      logins.value = loginData?.records ?? []
    } catch (err) {
      error.value = err
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  function startAutoRefresh() {
    stopAutoRefresh()
    if (interval > 0) {
      timerId = setInterval(load, interval)
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
    events,
    schedule,
    logins,
    reload: load,
    startAutoRefresh,
    stopAutoRefresh,
  }
}

export default { useSystemEvents }
