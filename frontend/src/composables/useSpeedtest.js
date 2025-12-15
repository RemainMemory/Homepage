import { ref } from 'vue'
import { runSpeedtest } from '../api/network'

export function useSpeedtest() {
  const running = ref(false)
  const error = ref(null)
  const result = ref(null)

  async function run() {
    if (running.value) return
    running.value = true
    error.value = null
    try {
      result.value = await runSpeedtest()
    } catch (err) {
      error.value = err
      console.error(err)
    } finally {
      running.value = false
    }
  }

  return {
    running,
    error,
    result,
    run,
  }
}

export default { useSpeedtest }
