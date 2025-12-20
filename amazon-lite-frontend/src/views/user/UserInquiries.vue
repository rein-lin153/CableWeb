<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900">我的询价单</h1>
        <p class="mt-2 text-sm text-gray-500">查看历史报价记录，或发起新的定制需求。</p>
      </div>
      
      <button 
        @click="showSmartInquiry = true"
        class="inline-flex items-center px-6 py-3 border border-transparent rounded-full shadow-sm text-base font-bold text-white bg-orange-600 hover:bg-orange-700 transition-all hover:scale-105"
      >
        <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
        发起智能询价
      </button>
    </div>

    <div class="bg-white shadow-sm rounded-xl border border-gray-100 overflow-hidden">
      <div v-if="!loading && inquiries.length === 0" class="p-12 text-center">
        <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900">暂无询价记录</h3>
        <p class="mt-1 text-gray-500">如果您有特殊的规格需求或项目清单，请发起询价。</p>
        <div class="mt-6">
          <button @click="showSmartInquiry = true" class="text-orange-600 font-bold hover:underline">立即发起 &rarr;</button>
        </div>
      </div>

      <ul v-else class="divide-y divide-gray-100">
        <li v-for="inquiry in inquiries" :key="inquiry.id" class="p-6 hover:bg-gray-50 transition-colors">
          <div class="flex flex-col sm:flex-row justify-between gap-4">
            
            <div class="flex-1">
              <div class="flex items-center mb-2">
                <span class="text-lg font-bold text-gray-900 mr-3">#{{ String(inquiry.id).padStart(5, '0') }}</span>
                <span 
                  class="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wide"
                  :class="getStatusClass(inquiry.status)"
                >
                  {{ getStatusLabel(inquiry.status) }}
                </span>
              </div>
              
              <div class="text-sm text-gray-600 mb-3 line-clamp-2">
                <span v-if="inquiry.items && inquiry.items.length > 0">
                  <span v-for="(item, idx) in inquiry.items" :key="item.id">
                    {{ item.product_name }} x{{ item.quantity }}<span v-if="idx < inquiry.items.length-1">, </span>
                  </span>
                </span>
                <span v-else-if="inquiry.user_remark">需求描述：{{ inquiry.user_remark }}</span>
                <span v-else>文件询价 (查看详情)</span>
              </div>
              
              <div class="text-xs text-gray-400">
                提交时间: {{ new Date(inquiry.created_at).toLocaleString() }}
              </div>
            </div>

            <div class="flex flex-col items-start sm:items-end justify-between min-w-[120px]">
              <div v-if="inquiry.quoted_total_price" class="mb-2 text-right">
                <p class="text-xs text-gray-500">出厂报价</p>
                <p class="text-xl font-bold text-green-600 font-mono">¥{{ inquiry.quoted_total_price.toLocaleString() }}</p>
              </div>
              <div v-else class="mb-2 text-right">
                <p class="text-xs text-gray-400">正在核算中...</p>
              </div>

              <div v-if="inquiry.admin_reply" class="text-xs text-orange-600 bg-orange-50 px-2 py-1 rounded max-w-xs text-right">
                经理留言: {{ inquiry.admin_reply }}
              </div>
            </div>

          </div>
        </li>
      </ul>
    </div>

    <SmartInquiryModal :is-open="showSmartInquiry" @close="handleCloseModal" />
    
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../api/axios';
import SmartInquiryModal from '../../components/SmartInquiryModal.vue';

const inquiries = ref([]);
const loading = ref(false);
const showSmartInquiry = ref(false);

const fetchInquiries = async () => {
  loading.value = true;
  try {
    const res = await api.get('/inquiries/');
    inquiries.value = res.data;
  } catch (e) {
    // 错误由 axios 拦截器处理
  } finally {
    loading.value = false;
  }
};

const handleCloseModal = () => {
  showSmartInquiry.value = false;
  // 提交回来后，刷新列表
  fetchInquiries();
};

const getStatusClass = (status) => {
  return status === 'quoted' 
    ? 'bg-green-100 text-green-700' 
    : 'bg-yellow-100 text-yellow-700';
};

const getStatusLabel = (status) => {
  const map = {
    pending: '待报价',
    quoted: '已报价',
    completed: '已完成'
  };
  return map[status] || status;
};

onMounted(fetchInquiries);
</script>