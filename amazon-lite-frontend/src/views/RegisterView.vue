<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="flex justify-center">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center shadow-lg shadow-orange-500/30">
          <svg class="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
        </div>
      </div>
      <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
        注册采购账号
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        已有账号？
        <router-link to="/login" class="font-medium text-orange-600 hover:text-orange-500">立即登录</router-link>
      </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10 border border-gray-100">
        <form class="space-y-6" @submit.prevent="handleRegister">
          
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">邮箱 / 手机号</label>
            <div class="mt-1">
              <input id="email" v-model="form.email" name="email" type="text" required class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm" placeholder="用于接收报价单">
            </div>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">设置密码</label>
            <div class="mt-1">
              <input id="password" v-model="form.password" name="password" type="password" required class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm">
            </div>
          </div>

          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700">确认密码</label>
            <div class="mt-1">
              <input id="confirmPassword" v-model="form.confirmPassword" name="confirmPassword" type="password" required class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm">
            </div>
          </div>

          <div>
            <button type="submit" :disabled="loading" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-gray-900 hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition-colors disabled:opacity-50">
              <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              {{ loading ? '注册中...' : '立即注册' }}
            </button>
          </div>
        </form>

        <div class="mt-6">
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-300"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-2 bg-white text-gray-500">遇到问题？</span>
            </div>
          </div>
          <div class="mt-4 text-center">
            <a href="tel:400-888-8888" class="text-orange-600 hover:text-orange-500 font-medium">电话联系客服开户 &rarr;</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '../composables/useAuth';

const router = useRouter();
const { register } = useAuth();
const loading = ref(false);

const form = reactive({
  email: '',
  password: '',
  confirmPassword: ''
});

const handleRegister = async () => {
  if (form.password !== form.formPassword) {
    if (form.password !== form.confirmPassword) {
      alert('两次输入的密码不一致');
      return;
    }
  }

  loading.value = true;
  try {
    // 自动填充 username 为 email，简化后端验证
    await register({
      username: form.email.split('@')[0] + '_' + Math.floor(Math.random() * 1000), // 随机用户名
      email: form.email,
      password: form.password,
      // 默认 role: 'customer'
    });
    alert('注册成功！');
    router.push('/');
  } catch (error) {
    console.error(error);
    alert('注册失败: ' + (error.response?.data?.detail || '未知错误'));
  } finally {
    loading.value = false;
  }
};
</script>