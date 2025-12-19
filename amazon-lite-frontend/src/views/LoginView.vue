<template>
  <div class="min-h-screen flex bg-white">
    
    <div class="hidden lg:flex lg:w-1/2 relative bg-gray-900 overflow-hidden">
      <img 
        src="https://images.unsplash.com/photo-1590959651367-692f36f045ce?q=80&w=2070&auto=format&fit=crop" 
        alt="Industrial Background" 
        class="absolute inset-0 w-full h-full object-cover opacity-60"
      >
      <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent flex flex-col justify-end p-16 text-white">
        <h2 class="text-4xl font-bold mb-4">连接世界的核心力量</h2>
        <p class="text-lg text-gray-300">Amazon Cable 致力于为全球基础设施提供最安全、高效的传输方案。</p>
      </div>
    </div>

    <div class="flex-1 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-20 xl:px-24 bg-white relative">
      <div class="mx-auto w-full max-w-sm lg:w-96 mt-20 lg:mt-0">
        
        <div class="text-left mb-10">
          <h2 class="text-3xl font-bold text-gray-900">欢迎回来</h2>
          <p class="mt-2 text-sm text-gray-600">
            请登录您的企业账户以查看报价
          </p>
        </div>

        <div class="mt-8">
          <form @submit.prevent="handleLogin" class="space-y-6">
            
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700">企业邮箱</label>
              <div class="mt-1">
                <input 
                  id="email" 
                  name="email" 
                  type="email" 
                  autocomplete="email" 
                  required 
                  v-model="email"
                  class="appearance-none block w-full px-3 py-3 border border-gray-300 rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 sm:text-sm transition-all"
                  placeholder="name@company.com"
                >
              </div>
            </div>

            <div class="space-y-1">
              <label for="password" class="block text-sm font-medium text-gray-700">密码</label>
              <div class="mt-1">
                <input 
                  id="password" 
                  name="password" 
                  type="password" 
                  autocomplete="current-password" 
                  required 
                  v-model="password"
                  class="appearance-none block w-full px-3 py-3 border border-gray-300 rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 sm:text-sm transition-all"
                >
              </div>
            </div>

            <div>
              <button 
                type="submit" 
                :disabled="loading"
                class="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white bg-gray-900 hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:-translate-y-0.5"
              >
                {{ loading ? '验证中...' : '安全登录' }}
              </button>
            </div>
            
            <div v-if="errorMsg" class="rounded-md bg-red-50 p-4 border border-red-100 animate-pulse">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="ml-3">
                  <h3 class="text-sm font-medium text-red-800">{{ errorMsg }}</h3>
                </div>
              </div>
            </div>

          </form>

          <div class="mt-8 text-center">
            <p class="text-sm text-gray-600">
              还没有企业账户？
              <router-link to="/register" class="font-medium text-orange-600 hover:text-orange-500 underline">
                立即注册供应商账户
              </router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
// 【关键修改】引入 useAuth 钩子
import { useAuth } from '../composables/useAuth';

const email = ref('');
const password = ref('');
const loading = ref(false);
const errorMsg = ref('');
const router = useRouter();

// 解构出 login 方法
const { login } = useAuth();

const handleLogin = async () => {
  loading.value = true;
  errorMsg.value = '';

  try {
    // 【关键修改】调用 useAuth 里的 login，而不是自己发请求
    // 这样 useAuth 内部的 isLoggedIn 状态才会变成 true，Navbar 才会更新
    await login(email.value, password.value);
    
    // 登录成功，跳转首页
    router.push('/');
    
  } catch (error) {
    console.error(error);
    // 处理 401 错误
    if (error.response && error.response.status === 401) {
      errorMsg.value = '邮箱或密码错误，请重试。';
    } else {
      errorMsg.value = '登录服务暂不可用，请稍后联系管理员。';
    }
  } finally {
    loading.value = false;
  }
};
</script>