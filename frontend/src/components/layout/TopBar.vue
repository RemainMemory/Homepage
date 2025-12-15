<template>
  <header class="top-bar glass-weak">
    <div class="top-bar__left">
      <h1 class="top-bar__title">主机监控</h1>
      <p class="top-bar__subtitle">实时查看系统 / 网络 / 外部服务状态</p>
    </div>
    <div class="top-bar__center">
      <form ref="searchBarRef" class="search-bar" @submit.prevent="submitSearch">
        <div class="search-field">
          <div class="search-selector" @click.stop="toggleMenu">
            <img :src="currentEngine.icon" :alt="currentEngine.name" />
            <span class="selector-caret">⌄</span>
          </div>
          <input
            type="search"
            v-model="searchText"
            placeholder="搜索系统 / 服务 / 资料..."
            aria-label="搜索"
          />
          <ul v-if="showMenu" class="selector-menu">
            <li
              v-for="engine in SEARCH_ENGINES"
              :key="engine.id"
              :class="{ active: engine.id === selectedEngine }"
              @click.stop="selectEngine(engine.id)"
            >
              <img :src="engine.icon" :alt="engine.name" />
              <span class="menu-label">{{ engine.name }}</span>
              <span v-if="engine.id === selectedEngine" class="menu-check">✓</span>
            </li>
          </ul>
        </div>
        <button type="submit">搜索</button>
      </form>
    </div>
    <div class="top-bar__right">
      <div class="pill">
        <span class="pill-dot"></span>
        <span>Backend: /host/overview</span>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const SEARCH_ENGINES = [
  {
    id: 'google',
    name: 'Google',
    icon: 'https://www.google.com/favicon.ico',
    buildUrl: (q) => `https://www.google.com/search?q=${encodeURIComponent(q)}`,
  },
  {
    id: 'bing',
    name: 'Bing',
    icon: 'https://www.bing.com/favicon.ico',
    buildUrl: (q) => `https://www.bing.com/search?q=${encodeURIComponent(q)}`,
  },
  {
    id: 'baidu',
    name: 'Baidu',
    icon: 'https://www.baidu.com/favicon.ico',
    buildUrl: (q) => `https://www.baidu.com/s?wd=${encodeURIComponent(q)}`,
  },
]

const selectedEngine = ref(SEARCH_ENGINES[0].id)
const searchText = ref('')
const showMenu = ref(false)
const searchBarRef = ref(null)

const currentEngine = computed(() => SEARCH_ENGINES.find((engine) => engine.id === selectedEngine.value) || SEARCH_ENGINES[0])

function submitSearch() {
  const query = searchText.value.trim()
  if (!query) return
  const url = currentEngine.value.buildUrl(query)
  window.open(url, '_blank', 'noopener')
  showMenu.value = false
}

function toggleMenu() {
  showMenu.value = !showMenu.value
}

function selectEngine(id) {
  selectedEngine.value = id
  showMenu.value = false
}

function handleClickOutside(event) {
  if (!searchBarRef.value) return
  if (!searchBarRef.value.contains(event.target)) {
    showMenu.value = false
  }
}

onMounted(() => {
  window.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  window.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.top-bar {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 0.8rem 1.2rem;
}

.top-bar__left {
  min-width: 0;
  flex: 1;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(15, 17, 23, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  padding: 0.4rem 0.75rem;
  width: 100%;
  justify-content: center;
}

.top-bar__center {
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 0 0 520px;
}

.top-bar__right {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  flex: 1;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(12, 16, 28, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  padding: 0.3rem 0.4rem 0.3rem 0.5rem;
  width: 100%;
  transition: border-color 0.25s ease, box-shadow 0.25s ease;
}

.search-bar:focus-within {
  border-color: rgba(59, 130, 246, 0.45);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35);
}

.search-field {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.25rem 0.5rem 0.25rem 0.35rem;
  border-radius: 999px;
  background: rgba(14, 16, 24, 0.6);
  position: relative;
  transition: background 0.2s ease;
}

.search-selector {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  background: rgba(255, 255, 255, 0.12);
  transition: background 0.2s ease, transform 0.2s ease;
}

.search-selector img {
  width: 18px;
  height: 18px;
  border-radius: 50%;
}

.selector-caret {
  position: absolute;
  right: -3px;
  bottom: -1px;
  font-size: 0.55rem;
  color: rgba(255, 255, 255, 0.85);
}

.search-selector:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.selector-menu {
  position: absolute;
  top: 110%;
  left: 0;
  background: rgba(12, 16, 28, 0.97);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  min-width: 160px;
  padding: 0.4rem 0;
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
  z-index: 10;
  animation: menuPop 0.16s ease;
}

.selector-menu li {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.75rem;
  cursor: pointer;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.85);
  transition: background 0.2s ease;
}

.selector-menu li:first-child {
  padding-top: 0.45rem;
}

.selector-menu li:last-child {
  padding-bottom: 0.45rem;
}

.selector-menu li img {
  width: 20px;
  height: 20px;
  border-radius: 50%;
}

.selector-menu li.active {
  background: rgba(59, 130, 246, 0.15);
}

.selector-menu li:hover {
  background: rgba(255, 255, 255, 0.1);
}

.menu-label {
  flex: 1;
}

.menu-check {
  font-size: 0.75rem;
  color: #93c5fd;
}

@keyframes menuPop {
  from {
    opacity: 0;
    transform: translate(-10px, -5px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translate(0, 0) scale(1);
  }
}

.search-field input {
  flex: 1;
  border: none;
  background: transparent;
  color: inherit;
  min-width: 0;
  font-size: 0.95rem;
}

.search-field input:focus {
  outline: none;
}

.search-bar button {
  border: none;
  background: #1d4ed8;
  color: #f8fbff;
  padding: 0.35rem 1.1rem;
  border-radius: 999px;
  font-size: 0.85rem;
  box-shadow: 0 8px 18px rgba(29, 78, 216, 0.35);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.search-bar button:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(29, 78, 216, 0.45);
}
</style>
