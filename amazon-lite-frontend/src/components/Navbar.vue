<template>
  <nav class="sticky top-0 z-50 border-b border-gray-200/60 bg-white/80 backdrop-blur-xl transition-all duration-300">
    <div class="max-w-[90rem] mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">

        <div class="flex items-center cursor-pointer group" @click="$router.push('/')">
          <div
            class="w-9 h-9 rounded-xl bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center mr-3 shadow-lg shadow-orange-500/20 group-hover:scale-105 transition-transform duration-300">
            <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div class="flex flex-col">
            <span class="font-extrabold text-xl tracking-tight text-gray-900 leading-none">Amazon<span
                class="text-orange-600">Cable</span></span>
            <span class="text-[10px] text-gray-400 font-medium tracking-widest uppercase">Industrial Solutions</span>
          </div>
        </div>

        <div class="hidden md:flex items-center space-x-8">
          <router-link v-for="link in navLinks" :key="link.path" :to="link.path"
            class="text-sm font-medium text-gray-600 hover:text-orange-600 transition-colors relative group py-2">
            {{ link.name }}
            <span
              class="absolute bottom-0 left-0 w-0 h-0.5 bg-orange-600 transition-all duration-300 group-hover:w-full"></span>
          </router-link>
        </div>

        <div class="flex items-center space-x-4">
          <button @click="toggleCart" class="relative p-2 text-gray-500 hover:text-orange-600 transition-colors group">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
            <span v-if="cartCount > 0"
              class="absolute top-0 right-0 inline-flex items-center justify-center px-1.5 py-0.5 text-xs font-bold leading-none text-white transform translate-x-1/4 -translate-y-1/4 bg-red-600 rounded-full border-2 border-white shadow-sm">
              {{ cartCount }}
            </span>
          </button>

          <div v-if="isLoggedIn" class="relative group">
            <button class="flex items-center space-x-2 focus:outline-none">
              <div
                class="w-9 h-9 rounded-full bg-gradient-to-tr from-gray-100 to-gray-200 border border-gray-200 flex items-center justify-center text-sm font-bold text-gray-600 shadow-sm group-hover:ring-2 ring-orange-100 transition-all">
                {{ userInitial }}
              </div>
            </button>

            <div
              class="absolute right-0 w-56 mt-2 origin-top-right bg-white divide-y divide-gray-100 rounded-xl shadow-xl ring-1 ring-black ring-opacity-5 focus:outline-none opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 transform z-50">
              <div class="px-4 py-3">
                <p class="text-xs text-gray-500">登录账号</p>
                <p class="text-sm font-bold text-gray-900 truncate">{{ user?.email }}</p>
              </div>

              <div class="py-1">
                <router-link to="/orders/my"
                  class="group flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-orange-50 hover:text-orange-700">
                  我的订单
                </router-link>
                <router-link to="/inquiries"
                  class="group flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-orange-50 hover:text-orange-700">
                  我的询价单
                </router-link>

                <router-link v-if="isAdmin" to="/admin/dashboard"
                  class="group flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-orange-50 hover:text-orange-700">
                  管理后台
                </router-link>
              </div>

              <div class="py-1">
                <button @click="logout"
                  class="group flex w-full items-center px-4 py-2 text-sm text-gray-700 hover:bg-red-50 hover:text-red-700 text-left">
                  退出登录
                </button>
              </div>
            </div>
          </div>

          <div v-else class="flex items-center space-x-2">
            <router-link to="/login" class="text-sm font-medium text-gray-500 hover:text-gray-900 px-3 py-2">
              登录
            </router-link>
            <router-link to="/register"
              class="text-sm font-medium text-white bg-gray-900 hover:bg-gray-800 px-4 py-2 rounded-lg shadow-md hover:shadow-lg transition-all">
              注册
            </router-link>
          </div>

          <div class="md:hidden flex items-center">
            <button @click="isMobileMenuOpen = !isMobileMenuOpen" class="text-gray-500 hover:text-gray-900 p-2">
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <transition enter-active-class="transition duration-200 ease-out"
      enter-from-class="transform -translate-y-2 opacity-0" enter-to-class="transform translate-y-0 opacity-100"
      leave-active-class="transition duration-150 ease-in" leave-from-class="transform translate-y-0 opacity-100"
      leave-to-class="transform -translate-y-2 opacity-0">
      <div v-if="isMobileMenuOpen" class="md:hidden bg-white border-t border-gray-100 shadow-lg">
        <div class="px-4 pt-2 pb-4 space-y-1">
          <router-link v-for="link in navLinks" :key="link.path" :to="link.path" @click="isMobileMenuOpen = false"
            class="block px-3 py-3 rounded-lg text-base font-medium text-gray-700 hover:bg-gray-50 hover:text-orange-600 transition-colors"
            active-class="bg-orange-50 text-orange-600 font-bold">
            {{ link.name }}
          </router-link>
          <router-link v-if="isLoggedIn" to="/inquiries" @click="isMobileMenuOpen = false"
            class="block px-3 py-3 rounded-lg text-base font-medium text-gray-700 hover:bg-gray-50 hover:text-orange-600 transition-colors">
            我的询价单
          </router-link>
        </div>
      </div>
    </transition>
  </nav>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '../composables/useAuth';
import { useCart } from '../composables/useCart';

const router = useRouter();
const { isLoggedIn, user, logout } = useAuth();
const { isCartOpen, cartItems } = useCart();

const isMobileMenuOpen = ref(false);

const navLinks = [
  { name: '首页', path: '/' },
  { name: '产品目录', path: '/products' },
  { name: '行业资讯', path: '/news' },
  { name: '技术参数', path: '/specs' },
];

const toggleCart = () => {
  isCartOpen.value = !isCartOpen.value;
};

const cartCount = computed(() => cartItems.value ? cartItems.value.length : 0);

const userInitial = computed(() => {
  if (user.value && (user.value.username || user.value.email)) {
    return (user.value.username || user.value.email).charAt(0).toUpperCase();
  }
  return 'U';
});

const isAdmin = computed(() => {
  const u = user.value;
  if (!u) return false;
  return u.role === 'admin' || u.is_admin === true;
});
</script>