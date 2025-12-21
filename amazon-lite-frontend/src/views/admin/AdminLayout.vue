<template>
  <div class="min-h-screen bg-gray-100 flex font-sans overflow-hidden">
    
    <transition name="fade">
      <div 
        v-if="isSidebarOpen" 
        @click="isSidebarOpen = false" 
        class="fixed inset-0 bg-black/50 z-40 md:hidden backdrop-blur-sm"
      ></div>
    </transition>

    <aside 
      class="fixed inset-y-0 left-0 z-50 w-64 bg-[#111827] text-white flex flex-col transition-transform duration-300 ease-in-out md:relative md:translate-x-0 flex-shrink-0 border-r border-gray-800"
      :class="isSidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div @click="navigate('/')"
        class="h-16 flex items-center px-6 border-b border-gray-800 hover:bg-gray-800 transition-colors cursor-pointer group">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center font-bold text-white shadow-lg">A</div>
          <span class="text-lg font-bold tracking-wide text-gray-100">Amazon <span class="text-orange-500">Admin</span></span>
        </div>
      </div>

      <nav class="flex-1 py-6 px-3 space-y-1 overflow-y-auto custom-scrollbar">
        <div v-for="(group, idx) in menuGroups" :key="idx" class="mb-6">
          <p class="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">{{ group.title }}</p>
          <router-link 
            v-for="item in group.items" 
            :key="item.path" 
            :to="item.path"
            @click="isSidebarOpen = false"
            class="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group mb-1 relative overflow-hidden"
            active-class="bg-orange-600 text-white shadow-lg shadow-orange-900/20"
            :class="$route.path === item.path ? '' : 'text-gray-400 hover:text-white hover:bg-gray-800'"
          >
            <span class="mr-3 opacity-80 group-hover:opacity-100 transition-opacity">{{ item.icon }}</span>
            {{ item.name }}
          </router-link>
        </div>
      </nav>

      <div class="p-4 border-t border-gray-800">
        <button @click="handleAdminLogout" class="flex items-center w-full px-4 py-2 text-sm font-medium text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors">
          <span class="mr-3">🚪</span> 退出管理
        </button>
      </div>
    </aside>

    <div class="flex-1 flex flex-col h-screen overflow-hidden bg-gray-50">
      <header class="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-4 md:px-8 shadow-sm z-10">
        <div class="flex items-center">
          <button @click="isSidebarOpen = !isSidebarOpen" class="md:hidden p-2 text-gray-500 hover:bg-gray-100 rounded-lg mr-4">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
            </svg>
          </button>
          <h1 class="text-lg font-bold text-gray-800">{{ currentRouteName }}</h1>
        </div>
        
        <div class="flex items-center gap-4">
          <div class="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center text-orange-600 font-bold text-xs border border-orange-200">
            AD
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8">
        <router-view v-slot="{ Component }">
          <transition name="scale" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAuth } from '../../composables/useAuth';
import { useRouter, useRoute } from 'vue-router';

const { logout } = useAuth();
const router = useRouter();
const route = useRoute();

const isSidebarOpen = ref(false);

const navigate = (path) => {
  router.push(path);
  isSidebarOpen.value = false;
};

const handleAdminLogout = async () => {
  await logout();
  router.push('/login');
};

const currentRouteName = computed(() => {
  const allItems = menuGroups.flatMap(g => g.items);
  const current = allItems.find(i => i.path === route.path);
  return current ? current.name : '控制台';
});

// 分组菜单
const menuGroups = [
  {
    title: '概览',
    items: [
      { name: '控制台', path: '/admin/dashboard', icon: '📊' }
    ]
  },
  {
    title: '交易中心',
    items: [
      { name: '订单管理', path: '/admin/orders', icon: '📦' },
      // 新增询价管理
      { name: '询价/报价', path: '/admin/inquiries', icon: '🏷️' },
    ]
  },
  {
    title: '商品与库存',
    items: [
      { name: '商品管理', path: '/admin/products', icon: '🔌' },
      { name: '分类管理', path: '/admin/categories', icon: '📑' },
      { name: '技术参数', path: '/admin/specs', icon: '📏' },
      { name: '成本核算', path: '/admin/costs', icon: '💰' },
    ]
  },
  {
    title: '用户与内容',
    items: [
      { name: '客户列表', path: '/admin/customers', icon: '👥' },
      { name: '员工管理', path: '/admin/employees', icon: '🪪' },
    ]
  }
];
</script>

<style scoped>
/* 简单的页面切换动画 */
.scale-enter-active,
.scale-leave-active {
  transition: all 0.2s ease;
}

.scale-enter-from,
.scale-leave-to {
  opacity: 0;
  transform: scale(0.98);
}
</style>