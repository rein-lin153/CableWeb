<template>
  <div class="flex flex-col h-full bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="px-6 py-5 border-b border-gray-100 flex flex-col sm:flex-row justify-between items-center gap-4 bg-white">
      <div class="flex items-center gap-4">
        <div class="p-2 bg-orange-100 rounded-lg">
          <svg class="w-6 h-6 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <h2 class="text-xl font-bold text-gray-900">询价报价管理</h2>
      </div>
      
      <div class="flex items-center gap-2">
        <select v-model="filterStatus" @change="fetchList" class="text-sm border-gray-200 rounded-lg focus:ring-orange-500 focus:border-orange-500 bg-gray-50 py-2 pl-3 pr-8">
          <option value="">全部状态</option>
          <option value="pending">待处理</option>
          <option value="quoted">已报价</option>
        </select>
        <button @click="fetchList" class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>

    <div class="flex-1 overflow-auto bg-gray-50">
      <div class="min-w-full inline-block align-middle">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50 sticky top-0 z-10 shadow-sm">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">询价单 ID</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">客户信息</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">需求概览</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">状态</th>
              <th scope="col" class="px-6 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-100">
            <tr v-for="item in list" :key="item.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-bold text-gray-900">#{{ String(item.id).padStart(5, '0') }}</div>
                <div class="text-xs text-gray-400 mt-1">{{ new Date(item.created_at).toLocaleDateString() }}</div>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center">
                  <div class="h-8 w-8 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center text-xs font-bold text-gray-600 mr-3">
                    {{ (item.user_email || '?').charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <div class="text-sm font-medium text-gray-900">{{ item.user_email || '未知用户' }}</div>
                    <div class="text-xs text-gray-500">用户 ID: {{ item.user_id }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="max-w-xs">
                  <div class="text-sm text-gray-900 line-clamp-2">
                    <span v-for="(line, idx) in item.items" :key="line.id">
                      {{ line.product_name }} <span class="text-gray-400">x{{ line.quantity }}</span>
                      <span v-if="idx < item.items.length - 1">, </span>
                    </span>
                  </div>
                  <div v-if="item.user_remark" class="mt-1.5 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                    备注: {{ item.user_remark }}
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2.5 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full"
                  :class="item.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'">
                  {{ item.status === 'pending' ? '待处理' : '已报价' }}
                </span>
                <div v-if="item.quoted_total_price" class="text-xs font-mono font-bold text-green-600 mt-1">
                  ¥{{ item.quoted_total_price.toLocaleString() }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button 
                  @click="openQuote(item)" 
                  class="text-orange-600 hover:text-orange-900 bg-orange-50 hover:bg-orange-100 px-3 py-1.5 rounded-lg transition-colors font-semibold"
                >
                  {{ item.status === 'pending' ? '立即报价' : '修改报价' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      <div @click="showModal = false" class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm"></div>
      
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg z-10 overflow-hidden transform transition-all">
        <div class="px-6 py-4 bg-gray-50 border-b border-gray-100 flex justify-between items-center">
          <h3 class="text-lg font-bold text-gray-900">报价处理 #{{ activeItem ? String(activeItem.id).padStart(5, '0') : '' }}</h3>
          <button @click="showModal = false" class="text-gray-400 hover:text-gray-500">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="p-6 space-y-6" v-if="activeItem">
          <div class="bg-blue-50/50 rounded-lg p-4 border border-blue-100">
            <h4 class="text-xs font-bold text-blue-700 uppercase tracking-wide mb-2">客户需求清单</h4>
            <ul class="space-y-2 max-h-40 overflow-y-auto custom-scrollbar">
              <li v-for="line in activeItem.items" :key="line.id" class="flex justify-between text-sm">
                <span class="text-gray-700">{{ line.product_name }} <span class="text-gray-400 text-xs">{{ line.product_spec }}</span></span>
                <span class="font-bold text-gray-900">x{{ line.quantity }}</span>
              </li>
            </ul>
          </div>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">总报价金额 (¥)</label>
              <div class="relative rounded-md shadow-sm">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span class="text-gray-500 sm:text-sm">¥</span>
                </div>
                <input 
                  v-model.number="form.quoted_total_price" 
                  type="number" 
                  class="block w-full pl-7 pr-12 py-2 border-gray-300 rounded-md focus:ring-orange-500 focus:border-orange-500 sm:text-sm shadow-sm"
                  placeholder="0.00"
                >
                <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                  <span class="text-gray-500 sm:text-sm">CNY</span>
                </div>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">销售留言/备注</label>
              <textarea 
                v-model="form.admin_reply" 
                rows="3" 
                class="block w-full border-gray-300 rounded-md focus:ring-orange-500 focus:border-orange-500 sm:text-sm shadow-sm p-2" 
                placeholder="例如：含税含运费，报价有效期3天..."
              ></textarea>
            </div>
          </div>
        </div>

        <div class="px-6 py-4 bg-gray-50 border-t border-gray-100 flex justify-end gap-3">
          <button @click="showModal = false" class="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500">
            取消
          </button>
          <button 
            @click="submitQuote" 
            :disabled="!form.quoted_total_price" 
            class="px-4 py-2 bg-orange-600 border border-transparent rounded-lg text-sm font-medium text-white hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
          >
            确认发送报价
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import api from '../../api/axios';
import { useToast } from '../../composables/useToast'; // 引入 Toast

const { success } = useToast();

const list = ref([]);
const filterStatus = ref("");
const showModal = ref(false);
const activeItem = ref(null);
const form = reactive({ quoted_total_price: null, admin_reply: '' });

const fetchList = async () => {
  try {
    const res = await api.get('/inquiries/', {
      params: { status: filterStatus.value || undefined }
    });
    list.value = res.data;
  } catch (e) { 
    // axios 拦截器会处理错误提示，这里不需要 catch alert
  }
};

const openQuote = (item) => {
  activeItem.value = item;
  form.quoted_total_price = item.quoted_total_price;
  form.admin_reply = item.admin_reply;
  showModal.value = true;
};

const submitQuote = async () => {
  try {
    await api.patch(`/inquiries/${activeItem.value.id}/quote`, form);
    showModal.value = false;
    fetchList();
    // 使用精美的 Toast 提示
    success('报价已发送');
  } catch (e) {
    // 留空，让 axios 拦截器处理
  }
};

onMounted(fetchList);
</script>