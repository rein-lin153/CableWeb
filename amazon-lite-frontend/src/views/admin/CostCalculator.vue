<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">💰 成本与报价管理</h1>
        <p class="text-sm text-gray-500 mt-1">
          当前铜价: <span class="text-red-600 font-bold" v-if="currentMarketPrice">¥{{ currentMarketPrice }}</span>
          <span v-else>未获取</span>
          <span class="mx-2">|</span>
          汇率: <span class="font-bold" v-if="currentRate">{{ currentRate }}</span>
        </p>
      </div>
      
      <div class="flex gap-3">
        <button 
          @click="syncPrices" 
          :disabled="syncing" 
          class="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded-lg shadow flex items-center gap-2 transition"
        >
          <span v-if="syncing">正在计算...</span>
          <span v-else>⚡ 按今日铜价重算</span>
        </button>
        
        <button @click="openCreate" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg shadow flex items-center gap-2 transition">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
          </svg>
          新建核算
        </button>
      </div>
    </div>

    <div class="bg-white p-4 rounded-lg shadow mb-6 flex flex-wrap gap-4 items-center">
      <div class="w-48">
        <label class="text-xs text-gray-500 font-bold">分类筛选</label>
        <select v-model="filterCategory" @change="fetchData" class="w-full border rounded p-2 text-sm bg-gray-50 focus:bg-white focus:ring-2 focus:ring-indigo-200 outline-none transition">
          <option value="">📂 全部分类</option>
          <option v-for="cat in categoryOptions" :key="cat" :value="cat">
            {{ cat }}
          </option>
        </select>
      </div>

      <div class="flex-1">
        <label class="text-xs text-gray-500 font-bold">搜索 (规格/备注)</label>
        <input v-model="searchQuery" @keyup.enter="fetchData" type="text" placeholder="输入关键字回车..." class="w-full border rounded p-2 text-sm focus:ring-2 focus:ring-indigo-200 outline-none">
      </div>
      
      <div class="self-end">
        <button @click="fetchData" class="bg-gray-100 hover:bg-gray-200 text-gray-600 px-4 py-2 rounded text-sm font-medium">
          刷新列表
        </button>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="th-std">规格/分类</th>
            <th class="th-std">原材料单价</th>
            <th class="th-std">总成本</th>
            <th class="th-std bg-yellow-50 text-yellow-700 border-l border-yellow-100">参考售价 (+15%)</th>
            <th class="th-std text-right">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="item in list" :key="item.id" class="hover:bg-gray-50 transition">
            <td class="px-6 py-4">
              <div class="font-bold text-gray-900">{{ item.spec_name }}</div>
              <div class="flex gap-1 mt-1">
                <span v-if="item.category" class="text-xs bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded border border-indigo-100">{{ item.category }}</span>
                <span v-if="item.material === 'Al'" class="text-xs bg-gray-200 text-gray-700 px-2 py-0.5 rounded border border-gray-300 ml-1">铝</span>
              </div>
              <div class="text-xs text-gray-400 mt-1 truncate max-w-[150px]" :title="item.remark">{{ item.remark }}</div>
            </td>
            
            <td class="px-6 py-4 text-sm">
               <div class="text-gray-400 text-xs mb-0.5">{{ item.material === 'Al' ? '铝' : '铜' }}价:</div>
               <div class="font-mono font-bold text-gray-700">${{ item.copper_price }}<span class="text-xs font-normal text-gray-400">/kg</span></div>
            </td>

            <td class="px-6 py-4">
               <div class="text-xs text-gray-400 mb-0.5">Total Cost</div>
               <div class="text-lg font-bold text-gray-700">${{ item.total_cost }}</div>
            </td>

            <td class="px-6 py-4 bg-yellow-50 border-l border-yellow-100">
               <div class="text-xs text-yellow-600 mb-0.5">建议零售价</div>
               <div class="text-xl font-black text-yellow-600">${{ item.reference_price }}</div>
            </td>

            <td class="px-6 py-4 text-right text-sm font-medium space-x-3">
              <button @click="openEdit(item)" class="text-indigo-600 hover:text-indigo-900">详情/编辑</button>
              <button @click="handleDelete(item.id)" class="text-red-600 hover:text-red-900">删除</button>
            </td>
          </tr>
          <tr v-if="list.length === 0">
            <td colspan="5" class="px-6 py-10 text-center text-gray-400">暂无数据，请先新建或刷新</td>
          </tr>
        </tbody>
      </table>
    </div>

    <CostCalculatorModal 
      :is-open="showModal" 
      :edit-data="currentEditItem"
      @close="showModal = false"
      @saved="handleSaved" 
    />

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from '../../api/axios'; // 根据你的实际路径调整
import CostCalculatorModal from '@/components/admin/CostCalculatorModal.vue';

const list = ref([]);
const categoryOptions = ref([]);
const filterCategory = ref('');
const searchQuery = ref('');

// 🟢 [新增] 同步相关状态
const syncing = ref(false);
const currentMarketPrice = ref(0);
const currentRate = ref(0);

const showModal = ref(false);
const currentEditItem = ref(null);

// 获取分类
const fetchCategories = async () => {
  try {
    const res = await axios.get('/admin/costs/categories');
    categoryOptions.value = res.data;
  } catch (e) {
    console.error("获取分类失败", e);
  }
};

// 获取列表数据
const fetchData = async () => {
  try {
    const params = {};
    if (filterCategory.value) params.category = filterCategory.value;
    if (searchQuery.value) params.search = searchQuery.value;
    
    const res = await axios.get('/admin/costs/', { params });
    list.value = res.data;
  } catch (e) {
    console.error(e);
  }
};

// 🟢 [新增] 一键同步铜价逻辑
const syncPrices = async () => {
  if(!confirm("⚠️ 确定要操作吗？\n\n系统将获取今日最新 [市场铜价]，并重新计算所有产品的：\n1. 原材料成本\n2. 建议零售价")) return;
  
  syncing.value = true;
  try {
    // 调用后端写好的 sync-market-prices 接口
    const res = await axios.post('/admin/costs/sync-market-prices');
    
    // 成功后提示
    alert(`✅ 同步成功！\n${res.data.message}\n当前铜价: ¥${res.data.market_cny}`);
    
    // 更新页面显示的行情数据
    currentMarketPrice.value = res.data.market_cny;
    currentRate.value = res.data.rate;
    
    // 刷新列表，显示最新价格
    await fetchData(); 
    
  } catch (e) {
    alert("❌ 同步失败: " + (e.response?.data?.detail || "请检查网络或后端日志"));
  } finally {
    syncing.value = false;
  }
};

const handleSaved = () => {
  fetchData();
  fetchCategories();
};

const openCreate = () => {
  currentEditItem.value = null;
  showModal.value = true;
};

const openEdit = (item) => {
  currentEditItem.value = { ...item };
  showModal.value = true;
};

const handleDelete = async (id) => {
  if(!confirm("确定删除该条成本记录吗？")) return;
  try {
    await axios.delete(`/admin/costs/${id}`);
    handleSaved(); // 删除后刷新
  } catch(e) {
    alert("删除失败");
  }
};

onMounted(() => {
  fetchData();
  fetchCategories();
});
</script>

<style scoped>
.th-std {
  @apply px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider;
}
</style>