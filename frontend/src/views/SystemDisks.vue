<template>
  <AppShell>
    <div class="dashboard system-disks">
      <header class="section-header">
        <div>
          <h1>磁盘与文件</h1>
          <p>查看已挂载磁盘、检测热插拔，并进行受限的文件浏览。</p>
        </div>
        <div class="section-header__actions">
          <button class="refresh-button" :disabled="loadingFiles || loadingDisks" @click="reload">
            <span class="refresh-button__icon" aria-hidden="true">⟳</span>
            <span>{{ loadingFiles || loadingDisks ? '刷新中...' : '刷新全部' }}</span>
          </button>
        </div>
      </header>

      <div v-if="error" class="dash-status dash-status--error">
        加载失败：{{ error.message }}
      </div>

      <section class="panel">
        <header class="panel-header">
          <div>
            <h2>磁盘设备</h2>
            <p>实时检测新增 / 移除的磁盘，突出可移动设备。</p>
          </div>
          <div class="disk-tags" v-if="addedDisks.length || removedDisks.length">
            <span v-for="device in addedDisks" :key="`add-${device}`" class="tag tag--add">
              + {{ device }}
            </span>
            <span v-for="device in removedDisks" :key="`rm-${device}`" class="tag tag--remove">
              − {{ device }}
            </span>
          </div>
        </header>

        <div v-if="loadingDisks && !diskList.length" class="dash-status">读取磁盘中...</div>
        <div v-else-if="!diskList.length" class="dash-status">未找到磁盘信息</div>

        <div class="disk-grid" v-else>
          <article v-for="disk in diskList" :key="disk.device" class="disk-card glass">
            <div class="disk-head">
              <div>
                <div class="disk-device">{{ disk.device }}</div>
                <div class="disk-mount">{{ disk.mount }}</div>
              </div>
              <span class="disk-fstype">{{ disk.fsType || '--' }}</span>
            </div>
            <div class="disk-usage">
              <strong>{{ formatPct(disk.usagePct) }}%</strong>
              <span>{{ disk.usedGb?.toFixed(1) ?? '--' }} / {{ disk.totalGb?.toFixed(1) ?? '--' }} GB</span>
            </div>
            <div class="disk-progress">
              <div class="disk-progress-fill" :style="{ width: `${clampPct(disk.usagePct)}%` }"></div>
            </div>
            <div class="disk-foot">
              <span>{{ disk.isRemovable ? '可移动设备' : '系统设备' }}</span>
              <span>剩余 {{ disk.freeGb?.toFixed(1) ?? '--' }} GB</span>
            </div>
          </article>
        </div>
      </section>

      <section class="panel">
        <header class="panel-header file-header">
          <div>
            <h2>文件浏览</h2>
            <p>受限在后端允许的根目录内，只读。</p>
          </div>
          <div class="file-actions">
            <button class="ghost-button" :disabled="!canNavigateUp || loadingFiles" @click="goParent">
              上一级
            </button>
            <button class="refresh-button refresh-button--compact" :disabled="loadingFiles" @click="browse(currentPath)">
              <span class="refresh-button__icon" aria-hidden="true">⟳</span>
              <span>{{ loadingFiles ? '载入中...' : '刷新目录' }}</span>
            </button>
          </div>
        </header>

        <div class="path-chip-row">
          <span class="path-label">当前路径</span>
          <code class="path-chip">{{ currentPath || '/' }}</code>
        </div>

        <div v-if="loadingFiles && !fileEntries.length" class="dash-status">加载目录中...</div>
        <div v-else-if="!fileEntries.length" class="dash-status">目录为空</div>

        <table v-else class="file-table">
          <thead>
            <tr>
              <th>名称</th>
              <th class="file-col-type">类型</th>
              <th class="file-col-size">大小</th>
              <th>路径</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="canNavigateUp" class="file-row--parent" @click="goParent">
              <td colspan="4">返回上一级</td>
            </tr>
            <tr
              v-for="entry in fileEntries"
              :key="entry.path"
              @dblclick="handleEntryClick(entry)"
            >
              <td>
                <span class="file-name" :class="{ 'is-dir': entry.is_dir }">{{ entry.name }}</span>
              </td>
              <td>{{ entry.is_dir ? '目录' : '文件' }}</td>
              <td>{{ entry.is_dir ? '-' : formatSize(entry.size) }}</td>
              <td class="file-path">{{ entry.path }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  </AppShell>
</template>

<script setup>
import { computed } from 'vue'
import AppShell from '../components/layout/AppShell.vue'
import { useSystemDisks } from '../composables/useSystemDisks'

const {
  disks,
  files,
  currentPath,
  loadingDisks,
  loadingFiles,
  error,
  browse,
  goParent,
  reload,
} = useSystemDisks('/')

const diskList = computed(() => {
  const list = disks.value?.devices ?? []
  return list.filter(shouldDisplayDisk)
})
const addedDisks = computed(() => disks.value?.added ?? [])
const removedDisks = computed(() => disks.value?.removed ?? [])
const fileEntries = computed(() => files.value?.entries ?? [])

const canNavigateUp = computed(() => {
  const path = currentPath.value
  if (!path || path === '/') return false
  return !/^[A-Za-z]:\\?$/.test(path)
})

function clampPct(value) {
  const num = Number(value)
  if (Number.isNaN(num)) return 0
  return Math.max(0, Math.min(100, num))
}

function formatPct(value) {
  if (value == null) return '--'
  return Number(value).toFixed(1)
}

function formatSize(size) {
  if (size == null) return '--'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let idx = 0
  let n = Number(size)
  while (n >= 1024 && idx < units.length - 1) {
    n /= 1024
    idx += 1
  }
  return `${n.toFixed(idx === 0 ? 0 : 1)} ${units[idx]}`
}

function handleEntryClick(entry) {
  if (entry.is_dir) {
    browse(entry.path)
  }
}

function shouldDisplayDisk(disk) {
  if (!disk) return false
  if (disk.isRemovable) return true

  const mount = (disk.mount || '').toLowerCase()
  const primaryMounts = ['/', '/data', '/system/volumes/data']
  if (primaryMounts.includes(mount)) return true

  // Windows 系统盘：C 或 C:\ 之类
  if (/^[a-z]:\\?$/.test(disk.mount || '')) return true

  // 过滤掉很小的系统辅助分区（通常 < 2GB）
  const total = Number(disk.totalGb ?? 0)
  if (Number.isFinite(total) && total >= 5) return true

  return false
}
</script>

<style scoped>
.system-disks {
  gap: 20px;
}

.ghost-button {
  border: 1px solid rgba(148, 163, 184, 0.4);
  background: transparent;
  color: #e2e8f0;
  padding: 6px 12px;
  border-radius: 999px;
}

.panel {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 1rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.disk-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.disk-card {
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 1rem;
  padding: 0.9rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  background: rgba(15, 23, 42, 0.45);
}

.disk-head {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  opacity: 0.85;
}

.disk-device {
  font-weight: 600;
}

.disk-mount {
  font-size: 0.78rem;
  opacity: 0.7;
}

.disk-fstype {
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 0.75rem;
}

.disk-usage {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-variant-numeric: tabular-nums;
}

.disk-progress {
  height: 8px;
  border-radius: 999px;
  background: rgba(71, 85, 105, 0.3);
  overflow: hidden;
}

.disk-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #38bdf8, #6366f1);
}

.disk-foot {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  opacity: 0.7;
}

.disk-tags {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.tag {
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.75rem;
  border: 1px solid;
}

.tag--add {
  border-color: rgba(16, 185, 129, 0.5);
  color: #34d399;
}

.tag--remove {
  border-color: rgba(248, 113, 113, 0.5);
  color: #f87171;
}

.file-header {
  flex-wrap: wrap;
  gap: 0.5rem;
}

.file-actions {
  display: flex;
  gap: 0.5rem;
}

.path-chip-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  font-size: 0.85rem;
}

.path-chip {
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(15, 23, 42, 0.45);
}

.file-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}

.file-table th,
.file-table td {
  padding: 0.45rem 0.25rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
  text-align: left;
}

.file-col-size {
  width: 120px;
}

.file-col-type {
  width: 80px;
}

.file-row--parent {
  cursor: pointer;
  color: #60a5fa;
}

.file-name.is-dir {
  color: #38bdf8;
}

.file-path {
  font-size: 0.78rem;
  opacity: 0.65;
  word-break: break-all;
}
</style>
