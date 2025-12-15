import { ref } from 'vue'
import {
  listDockerServices,
  createDockerService,
  updateDockerService,
  deleteDockerService,
} from '../api/docker'

export function useDockerServices() {
  const services = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function load() {
    loading.value = true
    error.value = null
    try {
      services.value = await listDockerServices()
    } catch (err) {
      error.value = err
    } finally {
      loading.value = false
    }
  }

  async function create(payload) {
    await createDockerService(payload)
    await load()
  }

  async function update(slug, payload) {
    await updateDockerService(slug, payload)
    await load()
  }

  async function remove(slug) {
    await deleteDockerService(slug)
    await load()
  }

  return {
    services,
    loading,
    error,
    load,
    create,
    update,
    remove,
  }
}
