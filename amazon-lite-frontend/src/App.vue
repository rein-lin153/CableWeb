<template>
  <div class="min-h-screen bg-gray-50 text-gray-900 font-sans">
    <Navbar />
    <router-view />
    <FloatingCart />
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue';
import FloatingCart from './components/FloatingCart.vue';
import { useAuth } from './composables/useAuth';
import { useCart } from './composables/useCart';
import { watch, onMounted } from 'vue';

const { isLoggedIn } = useAuth();
const { fetchCart } = useCart();

// 🟢 [核心修复] 
// 1. App 挂载时，如果已登录，立即拉取购物车
onMounted(() => {
  if (isLoggedIn.value) {
    fetchCart();
  }
});

// 2. 监听登录状态变化 (例如用户刚登录成功)，自动拉取
watch(isLoggedIn, (newVal) => {
  if (newVal) {
    fetchCart();
  } else {
    // 登出清空
    useCart().cartItems.value = [];
  }
});
</script>