<template>
  <div class="bg-gray-50/50 min-h-screen pt-24 pb-12">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
        <div>
          <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">我的询价单</h1>
          <p class="mt-1 text-sm text-gray-500">查看历史询价进度及销售报价</p>
        </div>
        <button 
          @click="$router.push('/products')" 
          class="group inline-flex items-center px-5 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-indigo-600 to-indigo-500 rounded-full shadow-lg hover:shadow-indigo-500/30 hover:-translate-y-0.5 transition-all duration-200"
        >
          <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          发起新询价
        </button>
      </div>

      <div v-if="loading" class="grid gap-6">
        <div v-for="i in 3" :key="i" class="h-32 bg-white rounded-2xl shadow-sm animate-pulse"></div>
      </div>
      
      <div v-else-if="inquiries.length === 0" class="flex flex-col items-center justify-center py-20 bg-white rounded-3xl shadow-sm border border-dashed border-gray-200">
        <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mb-4">
          <svg class="w-8 h-8 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <p class="text-lg font-medium text-gray-900">暂无询价记录</p>
        <p class="text-sm text-gray-500 mt-1">在购物车中点击"转询价单"即可发起</p>
      </div>

      <div v-else class="grid gap-6">
        <div 
          v-for="item in inquiries" 
          :key="item.id" 
          @click="openDetail(item)"
          class="group bg-white rounded-2xl shadow-sm hover:shadow-xl hover:shadow-indigo-500/5 border border-gray-100 overflow-hidden cursor-pointer transition-all duration-300 transform hover:-translate-y-1"
        >
          <div class="px-6 py-4 border-b border-gray-50 bg-gray-50/30 flex justify-between items-center">
            <div class="flex items-center gap-3">
              <span class="font-mono text-sm font-bold text-gray-500">#{{ String(item.id).padStart(5, '0') }}</span>
              <span class="text-xs text-gray-400">|</span>
              <span class="text-sm text-gray-500">{{ new Date(item.created_at).toLocaleString() }}</span>
            </div>
            <span 
              class="px-3 py-1 rounded-full text-xs font-bold border shadow-sm" 
              :class="getStatusClass(item.status)"
            >
              {{ formatStatus(item.status) }}
            </span>
          </div>
          
          <div class="p-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6">
            <div class="flex-1">
               <div class="flex items-center gap-2 mb-2">
                 <div class="p-1.5 bg-indigo-50 text-indigo-600 rounded-lg">
                   <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                     <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                   </svg>
                 </div>
                 <span class="text-sm font-medium text-gray-700">包含 {{ item.items?.length }} 种商品</span>
               </div>
               
               <p v-if="item.user_remark" class="text-sm text-gray-500 line-clamp-1 pl-8 relative">
                 <span class="absolute left-1 top-0 text-gray-300">↳</span>
                 备注: {{ item.user_remark }}
               </p>
            </div>

            <div v-if="item.status === 'quoted'" class="text-right">
              <p class="text-xs text-green-600 font-bold uppercase tracking-wider mb-1">已收到报价</p>
              <div class="text-2xl font-bold text-gray-900 font-mono">
                ¥{{ item.quoted_total_price.toLocaleString() }}
              </div>
            </div>
            <div v-else class="text-right">
               <span class="text-sm text-gray-400 italic">等待销售评估...</span>
            </div>
          </div>
          
          <div v-if="item.admin_reply" class="bg-green-50/50 px-6 py-3 border-t border-green-100 flex items-start gap-2">
            <svg class="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            <p class="text-sm text-green-800">
              <span class="font-bold">销售回复：</span>{{ item.admin_reply }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <Transition name="modal">
      <div v-if="selectedInquiry" class="fixed inset-0 z-[100] flex items-center justify-center px-4">
        <div @click="selectedInquiry = null" class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm transition-opacity"></div>
        
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden relative transform transition-all scale-100">
          
          <div class="px-6 py-5 border-b border-gray-100 flex justify-between items-center bg-gray-50/80 backdrop-blur">
            <div>
              <h3 class="text-lg font-bold text-gray-900">询价详情</h3>
              <p class="text-xs text-gray-500 font-mono mt-0.5">ID: #{{ String(selectedInquiry.id).padStart(5, '0') }}</p>
            </div>
            <button @click="selectedInquiry = null" class="text-gray-400 hover:text-gray-600 transition-colors p-2 hover:bg-gray-100 rounded-full">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="flex-1 overflow-y-auto p-6 space-y-6">
            <div v-if="selectedInquiry.user_remark" class="bg-amber-50 border border-amber-100 p-4 rounded-xl flex gap-3">
              <svg class="w-5 h-5 text-amber-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <div>
                <h4 class="text-xs font-bold text-amber-700 uppercase tracking-wide mb-1">我的备注</h4>
                <p class="text-sm text-amber-900">{{ selectedInquiry.user_remark }}</p>
              </div>
            </div>

            <div class="border rounded-xl overflow-hidden shadow-sm">
              <table class="min-w-full divide-y divide-gray-100">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">商品信息</th>
                    <th class="px-4 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">数量</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-100">
                  <tr v-for="line in selectedInquiry.items" :key="line.id" class="hover:bg-gray-50/50">
                    <td class="px-4 py-3">
                      <div class="font-bold text-gray-900">{{ line.product_name }}</div>
                      <div class="text-xs text-gray-500 mt-0.5 inline-flex items-center gap-1">
                        <span class="bg-gray-100 px-1.5 py-0.5 rounded">{{ line.product_spec }}</span>
                        <span class="bg-gray-100 px-1.5 py-0.5 rounded">{{ line.product_color }}</span>
                      </div>
                    </td>
                    <td class="px-4 py-3 text-right">
                      <span class="text-sm font-bold text-gray-900">x{{ line.quantity }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div v-if="selectedInquiry.status === 'quoted'" class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-5 border border-green-100">
              <h4 class="text-sm font-bold text-green-800 mb-3 flex items-center">
                <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                最终报价
              </h4>
              <div class="flex justify-between items-end">
                <p class="text-sm text-green-700">含税含运费</p>
                <p class="text-3xl font-extrabold text-green-600 font-mono">¥{{ selectedInquiry.quoted_total_price.toLocaleString() }}</p>
              </div>
            </div>
          </div>

          <div class="px-6 py-4 bg-gray-50 text-right border-t border-gray-100">
            <button @click="selectedInquiry = null" class="px-6 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 hover:text-gray-900 transition-colors">
              关闭
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api/axios';

const inquiries = ref([]);
const loading = ref(true);
const selectedInquiry = ref(null);

const fetchInquiries = async () => {
  try {
    const res = await api.get('/inquiries/');
    inquiries.value = res.data;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const formatStatus = (s) => {
  const map = { pending: '待报价', quoted: '已报价', accepted: '已接受', rejected: '已拒绝', closed: '已关闭' };
  return map[s] || s;
};

const getStatusClass = (s) => {
  const map = {
    pending: 'bg-yellow-50 text-yellow-700 border-yellow-200 ring-1 ring-yellow-200',
    quoted: 'bg-green-50 text-green-700 border-green-200 ring-1 ring-green-200',
    accepted: 'bg-blue-50 text-blue-700 border-blue-200 ring-1 ring-blue-200',
    closed: 'bg-gray-100 text-gray-500 border-gray-200 ring-1 ring-gray-200'
  };
  return map[s] || '';
};

const openDetail = (item) => {
  selectedInquiry.value = item;
};

onMounted(fetchInquiries);
</script>

<style scoped>
/* 简单的弹窗过渡动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .transform,
.modal-leave-active .transform {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-enter-from .transform,
.modal-leave-to .transform {
  transform: scale(0.95) translateY(10px);
  opacity: 0;
}
</style>