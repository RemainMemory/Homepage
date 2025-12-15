import http from './http'

export function fetchSystemSummary(params) {
  return http.get('/system/summary', params)
}

export function fetchSystemProcesses(params) {
  return http.get('/system/processes', params)
}

export function fetchSystemSensors() {
  return http.get('/system/sensors')
}

export function fetchSystemUptime() {
  return http.get('/system/uptime')
}

export function fetchSystemDisks() {
  return http.get('/system/disks')
}

export function fetchSystemFiles(params) {
  return http.get('/system/files', params)
}

export function fetchSystemEvents(params) {
  return http.get('/system/events', params)
}

export function fetchSystemResourceTrend(params) {
  return http.get('/system/resource-trend', params)
}

export function fetchSystemSchedule() {
  return http.get('/system/schedule')
}

export function fetchSystemLoginHistory(params) {
  return http.get('/system/security/logins', params)
}

export default {
  fetchSystemSummary,
  fetchSystemProcesses,
  fetchSystemSensors,
  fetchSystemUptime,
  fetchSystemDisks,
  fetchSystemFiles,
  fetchSystemEvents,
  fetchSystemResourceTrend,
  fetchSystemSchedule,
  fetchSystemLoginHistory,
}
