import http from './http'

export function fetchNetworkOverview() {
  return http.get('/network/overview')
}

export function fetchLanDevices() {
  return http.get('/network/lan-devices')
}

export function runSpeedtest() {
  return http.get('/network/speedtest')
}

export default {
  fetchNetworkOverview,
  fetchLanDevices,
  runSpeedtest,
}
