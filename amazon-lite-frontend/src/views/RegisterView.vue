<template>
  <div class="min-h-screen flex bg-white">
    
    <div class="hidden lg:flex lg:w-1/2 relative bg-gray-900 overflow-hidden">
      <img 
        src="https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?q=80&w=2070&auto=format&fit=crop" 
        alt="Manufacturing Background" 
        class="absolute inset-0 w-full h-full object-cover opacity-60"
      >
      <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent flex flex-col justify-end p-16 text-white">
        <h2 class="text-4xl font-bold mb-4">加入全球供应链</h2>
        <p class="text-lg text-gray-300">注册成为 Amazon Cable 的合作伙伴，获取即时库存报价与工程支持。</p>
      </div>
    </div>

    <div class="flex-1 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-20 xl:px-24 bg-white relative">
      
      <div class="mx-auto w-full max-w-sm lg:w-96 mt-20 lg:mt-0">
        <div class="text-left mb-10">
          <h2 class="text-3xl font-bold text-gray-900">创建新账户</h2>
          <p class="mt-2 text-sm text-gray-600">
            仅需几步即可完成企业认证
          </p>
        </div>

        <form @submit.prevent="handleRegister" class="space-y-6">
          
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">工作邮箱</label>
            <div class="mt-1">
              <input 
                v-model="email" 
                id="email" 
                name="email" 
                type="email" 
                required 
                class="appearance-none block w-full px-3 py-3 border border-gray-300 rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 sm:text-sm transition-all"
                placeholder="name@company.com"
              >
            </div>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">设置密码</label>
            <div class="mt-1">
              <input 
                v-model="password" 
                id="password" 
                name="password" 
                type="password" 
                required 
                class="appearance-none block w-full px-3 py-3 border border-gray-300 rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 sm:text-sm transition-all"
                placeholder="至少 6 位字符"
              >
            </div>
          </div>

          <div class="flex items-center">
            <input id="terms" name="terms" type="checkbox" required class="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded">
            <label for="terms" class="ml-2 block text-sm text-gray-900">
              我已阅读并同意 <a href="#" class="text-orange-600 hover:text-orange-500 font-medium">服务条款</a> 和 <a href="#" class="text-orange-600 hover:text-orange-500 font-medium">隐私协议</a>
            </label>
          </div>

          <div>
            <button 
              type="submit" 
              :disabled="loading" 
              class="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white bg-gray-900 hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:-translate-y-0.5"
            >
              {{ loading ? '正在创建...' : '立即注册' }}
            </button>
          </div>
          
          <div v-if="message" :class="`rounded-md p-4 mt-4 ${isError ? 'bg-red-50 text-red-800' : 'bg-green-50 text-green-800'}`">
             <div class="text-sm text-center font-medium">
               {{ message }}
             </div>
          </div>

        </form>

        <div class="mt-8 text-center">
          <p class="text-sm text-gray-600">
            已有账户？
            <router-link to="/login" class="font-medium text-orange-600 hover:text-orange-500 underline">
              直接登录
            </router-link>
          </p>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../api/axios';
import { useRouter } from 'vue-router';

const email = ref('');
const password = ref('');
const loading = ref(false);
const message = ref('');
const isError = ref(false);
const router = useRouter();

const handleRegister = async () => {
  loading.value = true;
  message.value = '';
  isError.value = false;

  try {
    await api.post('/auth/register', {
      email: email.value,
      password: password.value
    });
    
    message.value = '注册成功！正在跳转至登录页...';
    setTimeout(() => router.push('/login'), 1500);
    
  } catch (error) {
    isError.value = true;
    message.value = error.response?.data?.detail || '注册服务暂不可用，请稍后联系客服。';
  } finally {
    loading.value = false;
  }
};
</script>