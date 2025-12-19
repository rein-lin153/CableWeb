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

        <div class="hidden md:flex items-center space-x-1">
          <router-link v-for="link in navLinks" :key="link.path" :to="link.path"
            class="px-4 py-2 rounded-full text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100/80 transition-all duration-200"
            active-class="bg-gray-100 text-orange-600 font-bold">
            {{ link.name }}
          </router-link>
        </div>

        <div class="flex items-center space-x-3 md:space-x-5">

          <template v-if="!isLoggedIn">
            <div class="flex items-center space-x-3">
              <router-link to="/login" class="text-sm font-medium text-gray-500 hover:text-gray-900">登录</router-link>
              <span class="h-4 w-px bg-gray-300"></span>
              <router-link to="/register"
                class="hidden sm:block text-sm font-bold bg-gray-900 text-white px-5 py-2 rounded-full hover:bg-orange-600 hover:shadow-lg hover:shadow-orange-500/30 transition-all transform hover:-translate-y-0.5">
                注册企业账户
              </router-link>
              <router-link to="/register" class="sm:hidden text-sm font-bold text-orange-600">注册</router-link>
            </div>
          </template>

          <template v-else>
            <router-link v-if="isAdmin" to="/admin/dashboard"
              class="hidden md:flex items-center px-4 py-1.5 rounded-full text-xs font-bold text-white bg-gradient-to-r from-purple-600 to-indigo-600 shadow-md hover:shadow-lg hover:shadow-indigo-500/30 transition-all hover:scale-105">
              <svg class="w-3.5 h-3.5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
              控制台
            </router-link>

            <button @click="toggleCart" class="relative group p-2 rounded-full hover:bg-gray-100 transition-colors">
              <svg class="w-6 h-6 text-gray-600 group-hover:text-orange-600 transition-colors" fill="none"
                viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
              </svg>
              <span v-if="cartCount > 0"
                class="absolute top-1 right-1 h-4 min-w-[1rem] px-1 flex items-center justify-center text-[10px] font-bold text-white bg-red-500 rounded-full border-2 border-white shadow-sm">
                {{ cartCount }}
              </span>
            </button>

            <div class="relative ml-2 group" tabindex="0" @blur="closeDropdown">
              <button class="flex items-center space-x-2 focus:outline-none">
                <div
                  class="h-9 w-9 rounded-full bg-gray-100 flex items-center justify-center border border-gray-200 shadow-inner overflow-hidden">
                  <span class="text-sm font-bold text-gray-600">{{ userInitial }}</span>
                </div>
                <div class="hidden md:flex flex-col items-start text-xs">
                  <span class="font-bold text-gray-700 max-w-[5rem] truncate">{{ user?.username || '用户' }}</span>
                  <span v-if="isAdmin"
                    class="text-[10px] text-purple-600 bg-purple-50 px-1 rounded uppercase font-bold tracking-wide">ADMIN</span>
                  <span v-else-if="isDriver"
                    class="text-[10px] text-indigo-600 bg-indigo-50 px-1 rounded uppercase font-bold tracking-wide">DRIVER</span>
                </div>
              </button>

              <div
                class="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-xl py-2 border border-gray-100 opacity-0 invisible group-hover:opacity-100 group-hover:visible group-focus-within:opacity-100 group-focus-within:visible transition-all duration-200 transform origin-top-right z-50">
                <div class="px-4 py-3 border-b border-gray-50 bg-gray-50/50">
                  <p class="text-xs text-gray-400 uppercase tracking-wider mb-1">当前账号</p>
                  <p class="text-sm font-bold text-gray-900 truncate">{{ user?.email }}</p>
                </div>
                <div class="py-2">
                  <router-link to="/my-orders"
                    class="flex items-center px-4 py-2 text-sm text-gray-600 hover:bg-orange-50 hover:text-orange-700 transition-colors">
                    <svg class="w-4 h-4 mr-3 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
                    我的采购单
                  </router-link>
                  <router-link v-if="isAdmin" to="/admin/dashboard" class="flex md:hidden items-center px-4 py-2 text-sm text-purple-600 hover:bg-purple-50 font-bold">
                    <svg class="w-4 h-4 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" /></svg>
                    管理后台
                  </router-link>
                  <router-link v-if="isDriver" to="/driver" class="flex items-center px-4 py-2 text-sm text-indigo-600 hover:bg-indigo-50 font-bold">
                    <svg class="w-4 h-4 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                    派送员工作台
                  </router-link>
                </div>
                <div class="border-t border-gray-100 pt-2">
                  <button @click="handleLogout" class="w-full flex items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors">
                    <svg class="w-4 h-4 mr-3 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
                    退出登录
                  </button>
                </div>
              </div>
            </div>
          </template>

          <button @click="isMobileMenuOpen = !isMobileMenuOpen" class="md:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-100 focus:outline-none">
            <svg v-if="!isMobileMenuOpen" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <svg v-else class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

        </div>
      </div>
    </div>

    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="transform -translate-y-2 opacity-0"
      enter-to-class="transform translate-y-0 opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="transform translate-y-0 opacity-100"
      leave-to-class="transform -translate-y-2 opacity-0"
    >
      <div v-if="isMobileMenuOpen" class="md:hidden bg-white border-t border-gray-100 absolute top-16 left-0 w-full shadow-lg z-40">
        <div class="px-4 py-2 space-y-1">
          <router-link 
            v-for="link in navLinks" 
            :key="link.path" 
            :to="link.path"
            @click="isMobileMenuOpen = false"
            class="block px-4 py-3 rounded-lg text-base font-medium text-gray-600 hover:text-orange-600 hover:bg-orange-50 transition-colors"
            active-class="bg-orange-50 text-orange-600 font-bold"
          >
            {{ link.name }}
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

// 【新增】控制手机菜单开关
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
  return u.role === 'admin' || u.is_admin === true || u.is_superuser === true;
});

const isDriver = computed(() => {
  const u = user.value;
  if (!u) return false;
  return u.role === 'driver';
});

const handleLogout = () => {
  logout();
  router.push('/login');
};

const closeDropdown = (e) => {
  // 简单的失焦关闭逻辑
};
</script>