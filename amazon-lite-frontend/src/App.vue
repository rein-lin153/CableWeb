<template>
  <div class="antialiased text-gray-900">
    <ToastManager />

    <!-- 导航与购物车 -->
    <Navbar v-if="!$route.meta.hideNavbar" />
    <CartDrawer v-if="!$route.meta.hideNavbar" />
    
    <!-- 主体内容 -->
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>

    <!-- 全站悬浮联络栏：建议放在这里 -->
    <StickyContactBar v-if="!$route.meta.hideNavbar" />
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import Navbar from './components/Navbar.vue';
import CartDrawer from './components/CartDrawer.vue';
import ToastManager from './components/ToastManager.vue';
import StickyContactBar from './components/StickyContactBar.vue'; // 1. 导入组件
import { useAuth } from './composables/useAuth';

const { initializeAuth } = useAuth();

onMounted(() => {
  initializeAuth();
});
</script>