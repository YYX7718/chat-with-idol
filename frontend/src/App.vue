<template>
  <div id="app">
    <div class="app-container">
      <component :is="currentComponent" />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import Divination from './pages/divination.vue'
import IdolChat from './pages/idol-chat.vue'

const route = ref(getRoute())

const getComponent = {
  divination: Divination,
  chat: IdolChat
}

const currentComponent = computed(() => getComponent[route.value] || Divination)

function getRoute() {
  const hash = window.location.hash || ''
  if (hash.startsWith('#/chat')) return 'chat'
  if (hash.startsWith('#/divination')) return 'divination'
  return 'divination'
}

const onHashChange = () => {
  route.value = getRoute()
}

onMounted(() => {
  window.addEventListener('hashchange', onHashChange)
  route.value = getRoute()
})

onBeforeUnmount(() => {
  window.removeEventListener('hashchange', onHashChange)
})
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f5f5;
  color: #333;
}

#app {
  width: 100%;
  height: 100vh;
}

.app-container {
  width: 100%;
  height: 100%;
}
</style>
