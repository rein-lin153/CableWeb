<template>
  <div>
    <transition name="fade">
      <div v-if="isCartOpen" @click="close" class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-[60]"></div>
    </transition>

    <transition name="slide">
      <div v-if="isCartOpen" class="fixed inset-y-0 right-0 max-w-md w-full bg-white shadow-2xl z-[70] flex flex-col transform transition-transform duration-300 ease-in-out">
        
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gray-50/50">
          <h2 class="text-lg font-bold text-gray-900 flex items-center gap-2">
            <span>🛒</span> 购物车 ({{ cartItems.length }})
          </h2>
          <button @click="close" class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-6">
          <div v-if="cartItems.length === 0" class="flex flex-col items-center justify-center h-full text-gray-400 space-y-4">
            <svg class="w-16 h-16 text-gray-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
            <p>购物车是空的</p>
            <button @click="closeAndGo" class="text-indigo-600 font-bold hover:underline">去逛逛</button>
          </div>

          <div v-else class="space-y-4">
            <div v-for="item in cartItems" :key="item.id" class="flex gap-4 p-3 rounded-xl border border-gray-100 hover:border-indigo-100 hover:shadow-sm transition-all bg-white group">
              <div class="w-20 h-20 rounded-lg bg-gray-100 overflow-hidden flex-shrink-0 border border-gray-200">
                <img 
                  :src="item.image_url ? `http://192.168.1.76:8000${item.image_url}` : '/placeholder.jpg'" 
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                >
              </div>
              
              <div class="flex-1 flex flex-col justify-between">
                <div>
                  <h3 class="font-bold text-gray-900 line-clamp-1">{{ item.product_name }}</h3>
                  <p class="text-xs text-gray-500 mt-1">{{ item.spec }} | {{ item.color }}</p>
                </div>
                <div class="flex items-center justify-between mt-2">
                  <div class="text-indigo-600 font-bold font-mono">¥{{ item.price }} <span class="text-xs text-gray-400 font-normal">/{{ item.unit }}</span></div>
                  
                  <div class="flex items-center border border-gray-200 rounded-lg">
                    <button @click="updateQty(item, -1)" class="px-2 py-0.5 text-gray-500 hover:bg-gray-100 hover:text-indigo-600">-</button>
                    <span class="px-2 text-xs font-medium min-w-[1.5rem] text-center">{{ item.quantity }}</span>
                    <button @click="updateQty(item, 1)" class="px-2 py-0.5 text-gray-500 hover:bg-gray-100 hover:text-indigo-600">+</button>
                  </div>
                </div>
              </div>

              <button @click="removeItem(item.id)" class="text-gray-300 hover:text-red-500 self-start transition-colors">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div v-if="cartItems.length > 0" class="p-6 border-t border-gray-100 bg-white shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.1)] z-10">
          <div class="flex justify-between items-end mb-4">
            <span class="text-gray-500 text-sm">预估总价</span>
            <span class="text-2xl font-extrabold text-gray-900 font-mono">¥{{ cartTotal.toFixed(2) }}</span>
          </div>
          
          <div class="grid grid-cols-2 gap-3">
             

            <button 
              @click="checkout"
              class="flex justify-center items-center px-4 py-3 rounded-xl font-bold text-white bg-gray-900 hover:bg-black transition-all shadow-lg shadow-gray-200"
            >
              立即结算 <span class="ml-2">→</span>
            </button>
          </div>
          <p class="text-[10px] text-center text-gray-400 mt-3">大宗采购或特殊规格请选择“定做询价”</p>
        </div>
      </div>
    </transition>

    <transition name="modal">
      <div v-if="showInquiryModal" class="fixed inset-0 z-[80] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="showInquiryModal = false"></div>
        
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md relative overflow-hidden transform transition-all">
          <div class="px-6 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white flex justify-between items-center">
            <h3 class="text-lg font-bold flex items-center">
              <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              提交定做需求
            </h3>
            <button @click="showInquiryModal = false" class="text-white/80 hover:text-white">
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">技术要求 / 特殊规格</label>
              <textarea 
                v-model="inquiryForm.requirements"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                placeholder="例如：需要耐高温材质，符合 IEC 60502 标准，黑色护套..."
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">期望价格 / 折扣要求</label>
              <input 
                v-model="inquiryForm.targetPrice"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                placeholder="例如：定做8折，或者目标单价 50元/米"
              >
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">其他备注</label>
              <input 
                v-model="inquiryForm.remarks"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                placeholder="例如：加急订单，需要下周一发货"
              >
            </div>
          </div>

          <div class="px-6 py-4 bg-gray-50 flex justify-end gap-3">
            <button @click="showInquiryModal = false" class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-100">取消</button>
            <button @click="submitInquiry" class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 shadow-md">提交询价</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, ref, reactive } from 'vue';
import { useCart } from '../composables/useCart';
import { useRouter } from 'vue-router';
import api from '../api/axios';

const { isCartOpen, cartItems, removeItem, updateQuantity, fetchCart } = useCart();
const router = useRouter();

const close = () => { isCartOpen.value = false; };
const closeAndGo = () => { close(); router.push('/products'); };

// 询价表单状态
const showInquiryModal = ref(false);
const inquiryForm = reactive({
  requirements: '',
  targetPrice: '',
  remarks: ''
});

const cartTotal = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + (item.price * item.quantity), 0);
});

const updateQty = async (item, delta) => {
  const newQty = item.quantity + delta;
  if (newQty < 1) return;
  await updateQuantity(item.id, newQty);
};

const checkout = () => {
  close();
  router.push('/checkout');
};

const openInquiryModal = () => {
  showInquiryModal.value = true;
};

const submitInquiry = async () => {
  // 拼接用户输入的信息
  const parts = [];
  if (inquiryForm.requirements) parts.push(`[需求]: ${inquiryForm.requirements}`);
  if (inquiryForm.targetPrice) parts.push(`[期望]: ${inquiryForm.targetPrice}`);
  if (inquiryForm.remarks) parts.push(`[备注]: ${inquiryForm.remarks}`);
  
  const finalRemark = parts.join('; ') || '客户未填写备注';

  try {
    // 这里的参数结构已经符合后端要求 { user_remark: "..." }
    await api.post('/inquiries/', { user_remark: finalRemark });
    
    // 强制刷新购物车以清空前端状态
    await fetchCart();
    
    showInquiryModal.value = false;
    close();
    router.push('/inquiries');
    alert('✅ 询价单已提交！销售经理将根据您的“定做要求”核算最优报价。');
  } catch (e) {
    console.error(e);
    alert('提交失败: ' + (e.response?.data?.detail || '未知错误'));
  }
};
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-enter-active, .slide-leave-active { transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.slide-enter-from, .slide-leave-to { transform: translateX(100%); }

/* 模态框动画 */
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-active .transform, .modal-leave-active .transform { transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1); }
.modal-enter-from .transform, .modal-leave-to .transform { transform: scale(0.95) translateY(10px); }
</style>