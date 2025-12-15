<template>
  <div class="app-root">
    <div class="bg-overlay"></div>

    <div class="app-shell">
      <SideNav />

      <div class="app-main">
        <TopBar />
        <main class="app-content">
          <slot />
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import SideNav from './SideNav.vue'
import TopBar from './TopBar.vue'
</script>
