// 简单的 fetch 封装，你以后要加 token / 错误处理都在这里动

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`

  const resp = await fetch(
    url,
    {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    },
  )

  if (!resp.ok) {
    const text = await resp.text().catch(() => '')
    throw new Error(`HTTP ${resp.status}: ${text}`)
  }

  if (resp.status === 204) {
    return null
  }

  const text = await resp.text().catch(() => '')
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    return text
  }
}

export function get(path, params) {
  let fullPath = path
  if (params && Object.keys(params).length > 0) {
    const qs = new URLSearchParams(params).toString()
    fullPath = `${path}?${qs}`
  }
  return request(fullPath, { method: 'GET' })
}

export function post(path, body) {
  return request(path, { method: 'POST', body: JSON.stringify(body || {}) })
}

export function put(path, body) {
  return request(path, { method: 'PUT', body: JSON.stringify(body || {}) })
}

export function del(path) {
  return request(path, { method: 'DELETE' })
}

export default { get, post, put, del }
