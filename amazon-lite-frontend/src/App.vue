<template>
  <div class="antialiased text-gray-900">
    <ToastManager />

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
import { onMounted } from 'vue';
import Navbar from './components/Navbar.vue';
import CartDrawer from './components/CartDrawer.vue';
import ToastManager from './components/ToastManager.vue'; // 导入了组件
import { useAuth } from './composables/useAuth';

const { initializeAuth } = useAuth();

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