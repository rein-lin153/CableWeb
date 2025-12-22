<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-800 flex items-center">
          💰 成本与定价中心
          <span class="ml-3 text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full border border-indigo-200">
            利润保护系统 Active
          </span>
        </h1>
        <p class="text-sm text-gray-500 mt-1">
          基于今日铜价: <span class="text-red-600 font-bold font-mono">¥{{ currentMarketPrice }}</span>
          (汇率: {{ currentRate }}) | 系统将自动监测毛利风险
        </p>
      </div>

      <div class="flex gap-3">
        <button @click="syncPrices" :disabled="syncing" class="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded-lg shadow flex items-center gap-2 transition font-bold text-sm">
          <span v-if="syncing">正在从长江现货网获取...</span>
          <span v-else>⚡ 重算所有成本</span>
        </button>
        <button @click="openCreate" class="bg-gray-900 hover:bg-gray-800 text-white px-4 py-2 rounded-lg shadow flex items-center gap-2 transition font-bold text-sm">
          + 新建核算模型
        </button>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="th-std">规格模型</th>
            <th class="th-std">原材料成本 (Cost)</th>
            <th class="th-std bg-yellow-50/50 border-l border-yellow-100 text-yellow-700">建议售价 (+15%)</th>
            <th class="th-std bg-indigo-50/50 border-l border-indigo-100 text-indigo-700">当前线上售价</th>
            <th class="th-std text-right">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="item in list" :key="item.id" class="hover:bg-gray-50 transition">
            <td class="px-6 py-4">
              <div class="font-bold text-gray-900">{{ item.spec_name }}</div>
              <div class="text-xs text-gray-500 mt-1">{{ item.category }} | {{ item.material === 'Al'?'铝':'铜' }}</div>
            </td>

            <td class="px-6 py-4">
              <div class="flex flex-col">
                <span class="text-xs text-gray-400">Total Cost</span>
                <span class="text-lg font-mono font-bold text-gray-700">${{ item.total_cost }}</span>
              </div>
            </td>

            <td class="px-6 py-4 bg-yellow-50/30 border-l border-yellow-100">
              <div class="flex flex-col">
                <span class="text-xs text-yellow-600">Target Price</span>
                <span class="text-xl font-mono font-black text-yellow-600">${{ item.reference_price }}</span>
              </div>
            </td>

            <td class="px-6 py-4 bg-indigo-50/30 border-l border-indigo-100">
              <div v-if="getMatchedProduct(item)" class="flex flex-col">
                <div class="flex items-center justify-between">
                  <span class="text-xs text-indigo-600 truncate max-w-[120px]" :title="getMatchedProduct(item).name">
                    🔗 {{ getMatchedProduct(item).name }}
                  </span>
                </div>
                <div class="flex items-center gap-2 mt-0.5">
                  <span class="text-lg font-mono font-bold" 
                    :class="getMatchedProduct(item).price < item.reference_price ? 'text-red-600' : 'text-green-600'">
                    ${{ getMatchedProduct(item).price }}
                  </span>
                  <span v-if="getMatchedProduct(item).price < item.reference_price" class="text-[10px] bg-red-100 text-red-600 px-1.5 py-0.5 rounded font-bold animate-pulse">
                    低利风险
                  </span>
                </div>
                <button 
                  @click="syncPriceToProduct(item, getMatchedProduct(item))"
                  class="mt-2 text-xs bg-white border border-indigo-200 text-indigo-600 px-2 py-1 rounded shadow-sm hover:bg-indigo-50 transition-colors flex items-center justify-center"
                >
                  🔄 同步价格
                </button>
              </div>
              <div v-else class="text-xs text-gray-400 italic">
                未关联商品
                <button @click="openConvert(item)" class="ml-2 text-blue-500 hover:underline">去发布</button>
              </div>
            </td>

            <td class="px-6 py-4 text-right space-x-3">
              <button @click="openEdit(item)" class="text-gray-500 hover:text-indigo-600 font-medium text-sm">编辑</button>
              <button @click="handleDelete(item.id)" class="text-gray-400 hover:text-red-600 font-medium text-sm">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <CostCalculatorModal :is-open="showModal" :edit-data="currentEditItem" @close="showModal = false" @saved="handleSaved" />
    
    <div v-if="showConvertModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
       <div class="bg-white p-6 rounded-lg w-[400px]">
          <h3 class="font-bold text-lg mb-4">快速发布商品</h3>
          <p class="text-sm text-gray-500 mb-4">将 "{{ convertForm.name }}" 发布到前台？</p>
          <div class="flex justify-end gap-2">
            <button @click="showConvertModal=false" class="px-4 py-2 text-gray-500">取消</button>
            <button @click="handleConvert" class="px-4 py-2 bg-indigo-600 text-white rounded">确认发布</button>
          </div>
       </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import axios from '../../api/axios';
import CostCalculatorModal from '@/components/admin/CostCalculatorModal.vue';
import { useToast } from '../../composables/useToast';

const { success, error: showError } = useToast();
const list = ref([]);
const products = ref([]); // 缓存所有商品用于匹配
const syncing = ref(false);
const currentMarketPrice = ref(0);
const currentRate = ref(0);
const showModal = ref(false);
const currentEditItem = ref(null);

// 发布相关
const showConvertModal = ref(false);
const convertForm = reactive({ name: '' });

// 1. 获取成本列表
const fetchData = async () => {
  try {
    const res = await axios.get('/admin/costs/');
    list.value = res.data;
  } catch (e) { console.error(e); }
};

// 2. 获取商品列表 (用于智能匹配)
const fetchProducts = async () => {
  try {
    const res = await axios.get('/products/?limit=1000');
    products.value = res.data;
  } catch (e) { console.error(e); }
};

// 3. 智能匹配逻辑: 尝试通过名称模糊匹配
const getMatchedProduct = (costItem) => {
  // 规则：商品名包含规格名
  return products.value.find(p => p.name.includes(costItem.spec_name));
};

// 4. 同步价格: 将建议价写入商品表
const syncPriceToProduct = async (costItem, product) => {
  if (!confirm(`确认将商品 [${product.name}] 的价格更新为 $${costItem.reference_price} 吗？`)) return;
  
  try {
    // 假设后端有部分更新接口，或者我们更新整个对象
    // 这里演示更新主价格，也可以扩展为更新变体价格
    await axios.put(`/products/${product.id}`, { 
      ...product, // 保留原数据
      price: costItem.reference_price 
    });
    success(`✅ 价格已同步: $${costItem.reference_price}`);
    await fetchProducts(); // 刷新商品缓存
  } catch (e) {
    showError("同步失败");
  }
};

const syncPrices = async () => {
  if (!confirm("⚠️ 系统将获取今日最新 [市场铜价] 并重新计算所有成本。")) return;
  syncing.value = true;
  try {
    const res = await axios.post('/admin/costs/sync-market-prices');
    currentMarketPrice.value = res.data.market_cny;
    currentRate.value = res.data.rate;
    await fetchData();
    success("行情已更新，成本已重算");
  } catch (e) { showError("行情同步失败"); } finally { syncing.value = false; }
};

const handleSaved = () => { fetchData(); fetchProducts(); };
const openCreate = () => { currentEditItem.value = null; showModal.value = true; };
const openEdit = (item) => { currentEditItem.value = { ...item }; showModal.value = true; };
const handleDelete = async (id) => { if (confirm("删除此核算模型？")) { await axios.delete(`/admin/costs/${id}`); fetchData(); } };

// 简化的发布逻辑
const openConvert = (item) => { 
  convertForm.name = item.spec_name; 
  showConvertModal.value = true; 
};
const handleConvert = () => {
  // 实际需调用发布接口，这里仅做演示
  showConvertModal.value = false;
  success("功能演示：请使用完整发布弹窗");
};

onMounted(() => {
  fetchData();
  fetchProducts(); // 加载商品以进行比对
});
</script>

<style scoped>
.th-std { @apply px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider; }
</style>