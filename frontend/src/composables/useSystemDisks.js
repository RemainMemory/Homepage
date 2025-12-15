import { ref } from 'vue'
import { fetchSystemDisks, fetchSystemFiles } from '../api/system'

function normalizePath(path) {
  if (typeof path !== 'string' || path.length === 0) return '/'
  return path
}

function resolveParentPath(path) {
  const safePath = normalizePath(path)
  // Windows 根路径（C:\ 或 C:）直接返回自身
  if (/^[A-Za-z]:\\?$/.test(safePath)) {
    return safePath
  }
  if (safePath === '/') {
    return '/'
  }

  const isWindows = safePath.includes('\\')
  const segments = safePath.replace(/\\+/g, '/').split('/').filter(Boolean)
  segments.pop()
  const parent = isWindows ? segments.join('\\') : `/${segments.join('/')}`
  if (!parent) {
    return isWindows ? segments.join('\\') || safePath : '/'
  }
  return parent
}

export function useSystemDisks(initialPath = '/') {
  const disks = ref(null)
  const files = ref(null)
  const currentPath = ref(normalizePath(initialPath))

  const loadingDisks = ref(false)
  const loadingFiles = ref(false)
  const error = ref(null)

  async function loadDisks() {
    loadingDisks.value = true
    error.value = null
    try {
      disks.value = await fetchSystemDisks()
    } catch (err) {
      error.value = err
      console.error(err)
    } finally {
      loadingDisks.value = false
    }
  }

  async function browse(path = currentPath.value) {
    const nextPath = normalizePath(path)
    loadingFiles.value = true
    error.value = null
    try {
      const data = await fetchSystemFiles({ path: nextPath })
      files.value = data
      currentPath.value = data?.base_path || nextPath
    } catch (err) {
      error.value = err
      console.error(err)
    } finally {
      loadingFiles.value = false
    }
  }

  function goParent() {
    const parent = resolveParentPath(currentPath.value)
    if (parent && parent !== currentPath.value) {
      browse(parent)
    }
  }

  async function reloadAll() {
    await Promise.all([loadDisks(), browse(currentPath.value)])
  }

  loadDisks()
  browse(currentPath.value)

  return {
    disks,
    files,
    currentPath,
    loadingDisks,
    loadingFiles,
    error,
    loadDisks,
    browse,
    goParent,
    reload: reloadAll,
  }
}

export default { useSystemDisks }
