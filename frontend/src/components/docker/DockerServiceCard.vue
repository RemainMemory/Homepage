<template>
  <article
    class="docker-service-card"
    :class="{ 'docker-service-card--offline': !service.online }"
    @click="openPanel"
  >
    <div class="floating-controls">
      <span
        class="status-chip"
        :class="service.online ? 'status-chip--online' : 'status-chip--offline'"
      >
        <span class="status-dot" />
        {{ service.online ? '运行中' : '已离线' }}
      </span>
      <button class="card-edit" type="button" @click.stop="$emit('edit', service)" title="编辑">
        ✎
      </button>
    </div>
    <div class="service-icon" :class="{ 'service-icon--image': !!iconImage }">
      <img v-if="iconImage" :src="iconImage" :alt="`${service.name} logo`" />
      <span v-else>{{ iconLetter }}</span>
    </div>

    <div class="service-body">
      <div class="service-top">
        <div class="service-title">
          <h3>{{ service.name }}</h3>
          <p v-if="description" class="service-desc">{{ description }}</p>
        </div>
      </div>
      <div class="service-meta" v-if="metaBadges.length">
        <span v-for="badge in metaBadges" :key="badge">{{ badge }}</span>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  service: {
    type: Object,
    required: true,
  },
})

defineEmits(['edit'])

function openPanel() {
  if (!props.service.access_url) return
  window.open(props.service.access_url, '_blank', 'noreferrer noopener')
}

const description = computed(() => props.service.description || props.service.status_text || '')

const iconImage = computed(() => {
  const icon = props.service.icon
  if (icon && /^(https?:)?\/\//.test(icon)) {
    return icon
  }
  if (icon && icon.startsWith('data:')) {
    return icon
  }
  if (props.service.access_url) {
    try {
      const url = new URL(props.service.access_url)
      return `https://www.google.com/s2/favicons?sz=128&domain_url=${url.origin}`
    } catch (e) {
      // ignore invalid url
    }
  }
  return null
})

const iconLetter = computed(() => {
  const text = props.service.name?.trim()
  if (text) return text[0]?.toUpperCase()
  return 'D'
})

const hostDisplay = computed(() => {
  if (!props.service.access_url) return null
  try {
    const url = new URL(props.service.access_url)
    return url.hostname
  } catch (e) {
    return props.service.access_url
  }
})

const latencyDisplay = computed(() => {
  const latency = props.service.latency_ms
  if (latency === null || latency === undefined) return null
  if (latency >= 1000) return `${(latency / 1000).toFixed(1)}s`
  return `${latency.toFixed(1)}ms`
})

const badgeTag = computed(() => {
  if (props.service.tags && props.service.tags.length) {
    return props.service.tags[0]
  }
  if (props.service.container) {
    return props.service.container
  }
  return null
})

const metaBadges = computed(() => {
  return [hostDisplay.value, latencyDisplay.value, badgeTag.value].filter(Boolean)
})
</script>

<style scoped>
.docker-service-card {
  position: relative;
  display: flex;
  gap: 1rem;
  padding: 1.2rem 1.4rem;
  border-radius: 1.2rem;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: radial-gradient(circle at 0% 0%, rgba(59, 130, 246, 0.08), transparent 55%),
    linear-gradient(135deg, rgba(15, 23, 42, 0.94), rgba(17, 24, 39, 0.9));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02), 0 18px 40px rgba(2, 6, 23, 0.45);
  transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.3s ease;
  overflow: hidden;
}

.docker-service-card:hover {
  transform: translateY(-4px);
  border-color: rgba(96, 165, 250, 0.45);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04), 0 24px 50px rgba(15, 23, 42, 0.7);
}

.docker-service-card--offline {
  border-color: rgba(248, 113, 113, 0.3);
  background: radial-gradient(circle at 0% 0%, rgba(248, 113, 113, 0.08), transparent 55%),
    linear-gradient(135deg, rgba(24, 24, 35, 0.95), rgba(14, 19, 30, 0.92));
}

.floating-controls {
  position: absolute;
  top: 0.85rem;
  right: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  z-index: 4;
}

.card-edit {
  border: none;
  background: rgba(15, 23, 42, 0.45);
  border-radius: 999px;
  width: 28px;
  height: 28px;
  color: #cbd5f5;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.card-edit:hover {
  color: #f8fafc;
  background: rgba(59, 130, 246, 0.5);
}

.service-icon {
  width: 58px;
  height: 58px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.35rem;
  font-weight: 600;
  color: #e2e8f0;
  z-index: 2;
  transition: transform 0.25s ease;
}

.docker-service-card:hover .service-icon {
  transform: translateY(-2px);
}

.service-icon--image {
  padding: 6px;
  background: rgba(13, 16, 28, 0.85);
}

.service-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.service-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  z-index: 2;
  min-width: 0;
}

.service-top {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}


.service-title h3 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: #f1f5f9;
}

.service-desc {
  margin: 0.2rem 0 0;
  font-size: 0.82rem;
  color: rgba(226, 232, 240, 0.75);
}

.status-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.15rem 0.75rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
  border: 1px solid transparent;
  background: rgba(15, 23, 42, 0.9);
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.05);
}


.status-chip--online {
  color: #4ade80;
  border-color: rgba(34, 197, 94, 0.4);
  background: rgba(22, 101, 52, 0.35);
}

.status-chip--offline {
  color: #f87171;
  border-color: rgba(248, 113, 113, 0.45);
  background: rgba(127, 29, 29, 0.3);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 8px currentColor;
}

.service-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  font-size: 0.78rem;
  color: rgba(226, 232, 240, 0.7);
}

.service-meta span {
  position: relative;
  padding-left: 0.75rem;
}

.service-meta span:first-child {
  padding-left: 0;
}

.service-meta span:not(:first-child)::before {
  content: '•';
  position: absolute;
  left: 0;
  color: rgba(148, 163, 184, 0.4);
}
</style>
