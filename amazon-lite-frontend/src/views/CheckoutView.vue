<template>
  <div class="bg-gray-50 min-h-screen pt-24 pb-12">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <div class="flex items-center mb-8">
        <button @click="$router.back()" class="mr-4 p-2 rounded-full bg-white border border-gray-200 text-gray-500 hover:text-gray-900 transition-all">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
        </button>
        <div>
          <h1 class="text-2xl font-extrabold text-gray-900">生成报价单</h1>
          <p class="text-sm text-gray-500">Quotation Generation - 保存后可二次确认</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        <div class="lg:col-span-8 space-y-6">
          
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-100 bg-gray-50 flex items-center gap-2">
              <svg class="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              <h2 class="font-bold text-gray-900">报价单抬头 / 配送信息</h2>
            </div>
            <div class="p-6 space-y-4">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">联系人 <span class="text-red-500">*</span></label>
                  <input v-model="form.contactName" type="text" placeholder="例如：李工" class="w-full border-gray-300 rounded-lg focus:ring-orange-500 focus:border-orange-500 text-sm">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">联系电话 <span class="text-red-500">*</span></label>
                  <input v-model="form.contactPhone" type="tel" placeholder="用于接收报价单" class="w-full border-gray-300 rounded-lg focus:ring-orange-500 focus:border-orange-500 text-sm">
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">项目地址 / 收货地 (选填)</label>
                <textarea v-model="form.address" rows="2" placeholder="填写地址以便计算运费，生成更准确的报价单" class="w-full border-gray-300 rounded-lg focus:ring-orange-500 focus:border-orange-500 text-sm"></textarea>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-100 bg-gray-50 flex items-center gap-2">
              <svg class="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" /></svg>
              <h2 class="font-bold text-gray-900">预设结算方式</h2>
            </div>
            <div class="p-6">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <label class="relative flex items-center p-4 border rounded-xl cursor-pointer hover:bg-gray-50 transition-colors"
                  :class="form.paymentMethod === 'bank' ? 'border-orange-500 ring-1 ring-orange-500 bg-orange-50/20' : 'border-gray-200'">
                  <input type="radio" v-model="form.paymentMethod" value="bank" class="h-4 w-4 text-orange-600 border-gray-300 focus:ring-orange-500">
                  <div class="ml-3">
                    <span class="block text-sm font-bold text-gray-900">对公转账 / ABA</span>
                  </div>
                </label>
                <label class="relative flex items-center p-4 border rounded-xl cursor-pointer hover:bg-gray-50 transition-colors"
                  :class="form.paymentMethod === 'cod' ? 'border-orange-500 ring-1 ring-orange-500 bg-orange-50/20' : 'border-gray-200'">
                  <input type="radio" v-model="form.paymentMethod" value="cod" class="h-4 w-4 text-orange-600 border-gray-300 focus:ring-orange-500">
                  <div class="ml-3">
                    <span class="block text-sm font-bold text-gray-900">货到付款</span>
                  </div>
                </label>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
             <div class="px-6 py-4 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
               <h2 class="font-bold text-gray-900">报价清单内容</h2>
             </div>
             <div class="divide-y divide-gray-100">
                <div v-for="item in cartItems" :key="item.id" class="p-4 sm:p-6 flex gap-4">
                   <div class="w-16 h-16 sm:w-20 sm:h-20 bg-gray-100 rounded-lg border border-gray-200 flex-shrink-0 overflow-hidden">
                     <img :src="item.image_url" class="w-full h-full object-cover mix-blend-multiply">
                   </div>
                   <div class="flex-1">
                     <div class="flex justify-between items-start">
                       <div>
                         <h3 class="font-bold text-gray-900 text-sm sm:text-base">{{ item.product_name }}</h3>
                         <p class="text-xs text-gray-500 mt-1">{{ item.spec }} | {{ item.color }}</p>
                       </div>
                       <span class="font-mono font-bold text-gray-900">¥{{ (item.price * item.quantity).toFixed(2) }}</span>
                     </div>
                     <div class="flex justify-between items-center mt-4">
                       <span class="text-xs text-gray-400">单价: ¥{{ item.price }}</span>
                       <span class="text-xs font-bold bg-gray-100 px-2 py-1 rounded text-gray-600">x {{ item.quantity }} {{ item.unit }}</span>
                     </div>
                   </div>
                </div>
             </div>
          </div>
          
           <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
             <label class="block text-sm font-medium text-gray-700 mb-2">订单备注</label>
             <textarea v-model="form.note" rows="2" placeholder="例如：需要开具增值税发票，请备注..." class="w-full border-gray-300 rounded-lg focus:ring-orange-500 focus:border-orange-500 text-sm"></textarea>
          </div>

        </div>

        <div class="lg:col-span-4">
          <div class="bg-white rounded-xl shadow-lg border border-gray-100 p-6 sticky top-24">
             <h2 class="text-lg font-bold text-gray-900 mb-6">报价汇总</h2>
             
             <div class="space-y-3 pb-6 border-b border-gray-100 text-sm">
               <div class="flex justify-between text-gray-600">
                 <span>商品总额</span>
                 <span>¥{{ total.toFixed(2) }}</span>
               </div>
               <div class="flex justify-between text-gray-600">
                 <span>税费 (VAT)</span>
                 <span>待计算</span>
               </div>
             </div>

             <div class="flex justify-between items-end my-6">
               <span class="font-bold text-gray-900">参考总额</span>
               <span class="text-3xl font-black text-orange-600 font-mono">
                 ¥{{ total.toFixed(2) }}
               </span>
             </div>

             <button @click="submitOrder" :disabled="submitting || cartItems.length === 0"
               class="w-full py-4 bg-gray-900 hover:bg-orange-600 text-white rounded-xl font-bold text-lg shadow-xl shadow-gray-200 hover:shadow-orange-200 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center">
               <svg v-if="submitting" class="animate-spin h-5 w-5 mr-3 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
               <span v-else>保存报价单 (Save Quote)</span>
             </button>
             <p class="text-xs text-center text-gray-400 mt-4">点击保存后，您可以在订单中心确认并付款</p>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useCart } from '../composables/useCart';
import api from '../api/axios';

const router = useRouter();
const { cartItems, fetchCart } = useCart();
const submitting = ref(false);

const form = reactive({
  contactName: '',
  contactPhone: '',
  address: '',
  paymentMethod: 'bank',
  note: ''
});

const total = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + (item.price * item.quantity), 0);
});

onMounted(fetchCart);

const submitOrder = async () => {
  if (cartItems.value.length === 0) return;
  if (!form.contactName || !form.contactPhone) {
    alert('请填写联系人与电话，以便生成报价单');
    return;
  }

  submitting.value = true;
  try {
    const payload = {
      note: form.note ? `[报价单] ${form.note}` : '[报价单] 客户请求生成报价',
      shipping_address: form.address,
      contact_name: form.contactName,
      contact_phone: form.contactPhone,
      payment_method: form.paymentMethod
    };

    await api.post('/orders/', payload);

    await fetchCart(); 
    router.push('/orders/my'); // 跳转到订单列表
  } catch (e) {
    console.error(e);
    alert('生成报价单失败: ' + (e.response?.data?.detail || '网络错误'));
  } finally {
    submitting.value = false;
  }
};
</script>