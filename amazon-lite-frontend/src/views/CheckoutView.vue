<template>
  <div class="bg-gray-50/50 min-h-screen pt-24 pb-12">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center mb-8">
        <button 
          @click="$router.back()" 
          class="mr-4 p-2 rounded-full bg-white border border-gray-200 text-gray-500 hover:text-gray-900 hover:shadow-md transition-all duration-200"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </button>
        <h1 class="text-2xl font-extrabold text-gray-900 tracking-tight">订单结算</h1>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-50 bg-gray-50/50 flex justify-between items-center">
              <h2 class="font-bold text-gray-900 flex items-center gap-2">
                <svg class="w-5 h-5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                </svg>
                商品清单
              </h2>
              <span class="px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 text-xs font-bold">
                共 {{ cartItems.length }} 件
              </span>
            </div>
            
            <div class="divide-y divide-gray-100">
              <div v-if="cartItems.length === 0" class="p-12 text-center flex flex-col items-center">
                <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mb-4">
                  <svg class="w-8 h-8 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <p class="text-gray-500 font-medium">购物车是空的</p>
                <button @click="$router.push('/products')" class="mt-4 text-indigo-600 hover:underline text-sm">去选购商品</button>
              </div>
              
              <div v-else v-for="item in cartItems" :key="item.id" class="p-6 flex gap-5 group hover:bg-gray-50/50 transition-colors">
                <div class="w-24 h-24 bg-gray-100 rounded-xl overflow-hidden border border-gray-200 flex-shrink-0 relative">
                  <img 
                    :src="item.image_url ? `http://192.168.1.76:8000${item.image_url}` : '/placeholder.jpg'" 
                    class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  >
                </div>
                <div class="flex-1 flex flex-col justify-between py-1">
                  <div>
                    <div class="flex justify-between items-start">
                      <h3 class="font-bold text-gray-900 text-lg">{{ item.product_name }}</h3>
                      <span class="text-sm font-bold text-gray-900 bg-gray-100 px-2 py-1 rounded">x{{ item.quantity }}</span>
                    </div>
                    <p class="text-sm text-gray-500 mt-1 flex items-center gap-2">
                      <span class="bg-gray-100 px-1.5 py-0.5 rounded text-xs">{{ item.spec }}</span>
                      <span class="bg-gray-100 px-1.5 py-0.5 rounded text-xs">{{ item.color }}</span>
                    </p>
                  </div>
                  <div class="flex justify-between items-end">
                    <p class="text-xs text-gray-400">单价: ¥{{ item.price }} / {{ item.unit }}</p>
                    <span class="text-indigo-600 font-bold font-mono text-lg">¥{{ (item.price * item.quantity).toFixed(2) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="lg:col-span-1">
          <div class="bg-white rounded-2xl shadow-xl shadow-indigo-100/50 border border-gray-100 p-6 sticky top-24">
            <h2 class="font-bold text-gray-900 mb-6 text-lg flex items-center gap-2">
              <svg class="w-5 h-5 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              费用明细
            </h2>
            
            <div class="space-y-4 text-sm border-b border-gray-100 pb-6 mb-6">
              <div class="flex justify-between text-gray-600">
                <span>商品总价</span>
                <span class="font-medium">¥{{ total.toFixed(2) }}</span>
              </div>
              <div class="flex justify-between text-gray-600">
                <span>运费</span>
                <span class="text-green-600 font-medium bg-green-50 px-2 py-0.5 rounded text-xs">商家包邮</span>
              </div>
              <div class="flex justify-between text-gray-600">
                <span>会员折扣</span>
                <span class="text-orange-500">- ¥0.00</span>
              </div>
            </div>

            <div class="flex justify-between items-end mb-8">
              <div>
                <span class="block text-xs text-gray-400 mb-1">实付金额</span>
                <span class="font-bold text-gray-900 text-lg">CNY</span>
              </div>
              <span class="text-4xl font-extrabold text-orange-600 font-mono tracking-tight">¥{{ total.toFixed(2) }}</span>
            </div>

            <button 
              @click="submitOrder"
              :disabled="submitting || cartItems.length === 0"
              class="w-full py-4 bg-gray-900 hover:bg-black text-white rounded-xl font-bold text-lg shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center group"
            >
              <span v-if="submitting" class="flex items-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                正在提交...
              </span>
              <span v-else class="flex items-center">
                立即支付
                <svg class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </span>
            </button>
            
            <div class="mt-4 flex items-center justify-center gap-2 text-xs text-gray-400">
              <svg class="w-4 h-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>安全支付保障</span>
              <span class="w-1 h-1 bg-gray-300 rounded-full"></span>
              <span>支持对公转账</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useCart } from '../composables/useCart';
import api from '../api/axios';

const router = useRouter();
const { cartItems, fetchCart } = useCart();
const submitting = ref(false);

const total = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + (item.price * item.quantity), 0);
});

// 确保进入页面时数据是最新的
onMounted(fetchCart);

const submitOrder = async () => {
  if (cartItems.value.length === 0) return;
  
  submitting.value = true;
  try {
    // 调用后端创建订单接口
    await api.post('/orders/');
    
    // 下单成功后：刷新购物车 (前端清空) 并跳转
    await fetchCart();
    router.push('/orders/my');
    
    // 可以替换为更好看的 Toast 提示
    alert('🎉 下单成功！请留意发货通知。');
  } catch (e) {
    console.error(e);
    alert('下单失败: ' + (e.response?.data?.detail || '未知错误'));
  } finally {
    submitting.value = false;
  }
};
</script>