<template>
  <div class="min-h-screen bg-gray-100 flex font-sans overflow-hidden">
    
    <transition name="fade">
      <div 
        v-if="isSidebarOpen" 
        @click="isSidebarOpen = false" 
        class="fixed inset-0 bg-black/50 z-40 md:hidden"
      ></div>
    </transition>

    <aside 
      class="fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 text-white flex flex-col transition-transform duration-300 ease-in-out md:relative md:translate-x-0 flex-shrink-0"
      :class="isSidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div @click="navigate('/')"
        class="h-20 flex items-center justify-center border-b border-gray-800 hover:bg-gray-800 transition-colors cursor-pointer group">
        <div class="flex items-center">
          <img src="/logo.jpg" alt="Admin Logo"
            class="w-8 h-8 rounded-full mr-2 object-cover border border-gray-600 group-hover:border-orange-500 transition-colors">
          <span class="text-xl font-bold tracking-wider text-white">Amazon <span class="text-orange-500">Admin</span></span>
        </div>
      </div>

      <nav class="flex-1 py-6 px-3 space-y-1 overflow-y-auto custom-scrollbar">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path"
          :to="item.path" 
          @click="isSidebarOpen = false"
          active-class="bg-orange-600 text-white"
          class="flex items-center px-4 py-3 text-gray-400 hover:bg-gray-800 hover:text-white rounded-lg transition-all group"
        >
          <component :is="item.icon" class="w-5 h-5 mr-3" />
          <span class="font-medium">{{ item.name }}</span>
        </router-link>
      </nav>

      <div class="p-4 border-t border-gray-800">
        <button @click="handleAdminLogout"
          class="w-full flex items-center justify-center px-4 py-2 border border-gray-700 rounded-lg text-sm text-gray-400 hover:bg-red-900 hover:text-white transition-all">
          <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          安全退出
        </button>
      </div>
    </aside>

    <div class="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
      
      <header class="md:hidden h-16 bg-gray-900 flex items-center justify-between px-4 flex-shrink-0">
        <button @click="isSidebarOpen = true" class="p-2 text-gray-400 hover:text-white">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <span class="text-white font-bold">管理后台</span>
        <div class="w-10"></div> </header>

      <main class="flex-1 overflow-y-auto bg-gray-50 p-4 md:p-8">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuth } from '../../composables/useAuth';
import { useRouter } from 'vue-router';

const { logout } = useAuth();
const router = useRouter();

// 侧边栏开关状态
const isSidebarOpen = ref(false);

const navigate = (path) => {
  router.push(path);
  isSidebarOpen.value = false;
};

const handleAdminLogout = async () => {
  await logout();
  router.push('/login');
};

// 菜单数据化，方便维护
const menuItems = [
  { name: '控制台', path: '/admin/dashboard', icon: 'svg-dashboard' }, // 这里的 icon 可以替换为你的图标逻辑
  { name: '库存管理', path: '/admin/products', icon: 'svg-products' },
  { name: '分类管理', path: '/admin/categories', icon: 'svg-categories' },
  { name: '订单管理', path: '/admin/orders', icon: 'svg-orders' },
  { name: '客户列表', path: '/admin/customers', icon: 'svg-customers' },
  { name: '内部员工', path: '/admin/employees', icon: 'svg-employees' },
  { name: '国标参数', path: '/admin/specs', icon: 'svg-specs' },
  { name: '新闻资讯', path: '/admin/news', icon: 'svg-news' },
];
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 隐藏滚动条但保留滚动功能 */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #374151;
  border-radius: 10px;
}
</style>