import http from './http'

// 首页聚合接口
export function fetchHostOverview() {
  return http.get('/host/overview')
}
