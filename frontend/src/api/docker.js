import http from './http'

export function fetchDockerOverview() {
  return http.get('/docker/overview')
}

export function listDockerServices() {
  return http.get('/docker/services')
}

export function createDockerService(payload) {
  return http.post('/docker/services', payload)
}

export function updateDockerService(slug, payload) {
  return http.put(`/docker/services/${slug}`, payload)
}

export function deleteDockerService(slug) {
  return http.del(`/docker/services/${slug}`)
}
