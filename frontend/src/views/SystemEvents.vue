<template>
  <AppShell>
    <div class="dashboard system-events">
      <header class="section-header">
        <div>
          <h1>系统事件 / 登录</h1>
          <p>查看最新系统日志、计划任务与登录历史，帮助快速排查异常。</p>
        </div>
        <div class="section-header__actions">
          <button class="refresh-button" :disabled="loading" @click="reload">
            <span class="refresh-button__icon" aria-hidden="true">⟳</span>
            <span>{{ loading ? '刷新中...' : '刷新全部' }}</span>
          </button>
        </div>
      </header>

      <div v-if="error" class="dash-status dash-status--error">
        加载失败：{{ error.message }}
      </div>

      <section class="panel">
        <header class="panel-header">
          <div>
            <h2>最近事件</h2>
            <p>来自系统日志（journalctl / log show）。</p>
          </div>
        </header>

        <div v-if="loading && !events.length" class="dash-status">事件读取中...</div>
        <ul v-else-if="events.length" class="event-timeline">
          <li v-for="event in events" :key="event.timestamp + event.message">
            <span class="event-dot" :class="`event-dot--${event.level || 'info'}`"></span>
            <div class="event-content">
              <div class="event-header">
                <span class="event-time">{{ formatTime(event.timestamp) }}</span>
                <span class="event-source">{{ event.source || 'system' }}</span>
              </div>
              <p class="event-message">{{ event.message }}</p>
            </div>
          </li>
        </ul>
        <div v-else class="dash-status">暂无事件记录</div>
      </section>

      <section class="panel panel--split">
        <div class="sub-panel">
          <header>
            <h3>定时任务</h3>
            <p>当前用户的 crontab（Linux）。</p>
          </header>
          <ul v-if="schedule.length" class="schedule-list">
            <li v-for="item in schedule" :key="item.expression + item.command">
              <code class="cron-exp">{{ item.expression }}</code>
              <div class="cron-body">
                <div class="cron-command">{{ item.command }}</div>
                <div class="cron-comment" v-if="item.comment">{{ item.comment }}</div>
              </div>
            </li>
          </ul>
          <div v-else class="dash-status">未检测到定时任务</div>
        </div>

        <div class="sub-panel">
          <header>
            <h3>登录历史</h3>
            <p>last -n 输出（仅 Linux）。</p>
          </header>
          <table class="login-table" v-if="logins.length">
            <thead>
              <tr>
                <th>用户</th>
                <th>主机</th>
                <th>TTY</th>
                <th>时间</th>
                <th>时长</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="login in logins" :key="login.timestamp + login.username">
                <td>{{ login.username }}</td>
                <td>{{ login.host || '-' }}</td>
                <td>{{ login.tty || '-' }}</td>
                <td>{{ formatTime(login.timestamp) }}</td>
                <td>{{ login.duration || '-' }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else class="dash-status">暂无登录记录</div>
        </div>
      </section>
    </div>
  </AppShell>
</template>

<script setup>
import AppShell from '../components/layout/AppShell.vue'
import { useSystemEvents } from '../composables/useSystemEvents'

const { events, schedule, logins, loading, error, reload } = useSystemEvents()

function formatTime(ts) {
  if (!ts) return '--'
  const date = typeof ts === 'string' ? new Date(ts) : ts
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}
</script>

<style scoped>
.system-events {
  gap: 20px;
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

.event-timeline {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.event-timeline li {
  display: flex;
  gap: 0.75rem;
}

.event-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  margin-top: 0.3rem;
}

.event-dot--info {
  background: #38bdf8;
}

.event-dot--warning {
  background: #f97316;
}

.event-dot--error {
  background: #f87171;
}

.event-content {
  flex: 1;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 0.85rem;
  padding: 0.75rem;
  background: rgba(15, 23, 42, 0.4);
}

.event-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.82rem;
  opacity: 0.75;
}

.event-message {
  margin: 0.4rem 0 0;
  font-size: 0.9rem;
  line-height: 1.4;
}

.panel--split {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.sub-panel {
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 1rem;
  padding: 0.9rem;
  background: rgba(15, 23, 42, 0.4);
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.schedule-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.schedule-list li {
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 0.7rem;
  padding: 0.6rem;
  background: rgba(15, 23, 42, 0.3);
}

.cron-exp {
  font-size: 0.78rem;
  opacity: 0.75;
}

.cron-body {
  margin-top: 0.3rem;
}

.cron-command {
  font-size: 0.9rem;
  font-weight: 600;
}

.cron-comment {
  font-size: 0.78rem;
  opacity: 0.7;
}

.login-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.login-table th,
.login-table td {
  padding: 0.35rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.15);
  text-align: left;
}
</style>
