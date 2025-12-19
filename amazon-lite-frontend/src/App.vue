<template>
  <div class="antialiased text-gray-900">
    <Navbar v-if="!$route.meta.hideNavbar" />
    <CartDrawer v-if="!$route.meta.hideNavbar" />
    
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'; // 引入 onMounted
import Navbar from './components/Navbar.vue';
import CartDrawer from './components/CartDrawer.vue';
import { useAuth } from './composables/useAuth'; // 引入 Auth

const { initializeAuth } = useAuth(); // 获取初始化函数

// 【核心修复】App 挂载时，立即恢复用户状态
onMounted(() => {
  initializeAuth();
});
</script>
<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>