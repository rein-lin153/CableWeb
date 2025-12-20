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
        <button @click="syncPrices" :disabled="syncing"
          class="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded-lg shadow flex items-center gap-2 transition">
          <span v-if="syncing">正在计算...</span>
          <span v-else>⚡ 按今日铜价重算</span>
        </button>
        <button @click="openCreate"
          class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg shadow flex items-center gap-2 transition">
          新建核算
        </button>
      </div>
    </div>

    <div class="bg-white p-4 rounded-lg shadow mb-6 flex flex-wrap gap-4 items-center">
      <div class="w-48">
        <label class="text-xs text-gray-500 font-bold">分类筛选</label>
        <select v-model="filterCategory" @change="fetchData"
          class="w-full border rounded p-2 text-sm bg-gray-50 focus:bg-white focus:ring-2 focus:ring-indigo-200 outline-none transition">
          <option value="">📂 全部分类</option>
          <option v-for="cat in categoryOptions" :key="cat" :value="cat">{{ cat }}</option>
        </select>
      </div>
      <div class="flex-1">
        <label class="text-xs text-gray-500 font-bold">搜索 (规格/备注)</label>
        <input v-model="searchQuery" @keyup.enter="fetchData" type="text" placeholder="输入关键字回车..."
          class="w-full border rounded p-2 text-sm focus:ring-2 focus:ring-indigo-200 outline-none">
      </div>
      <div class="self-end">
        <button @click="fetchData"
          class="bg-gray-100 hover:bg-gray-200 text-gray-600 px-4 py-2 rounded text-sm font-medium">刷新</button>
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
            <th class="th-std">状态</th>
            <th class="th-std text-right">操作</th>
            
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="item in list" :key="item.id" class="hover:bg-gray-50 transition">
            <td class="px-6 py-4">
              <div class="font-bold text-gray-900">{{ item.spec_name }}</div>
              <div class="flex gap-1 mt-1">
                <span v-if="item.category"
                  class="text-xs bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded border border-indigo-100">{{
                  item.category }}</span>
                <span v-if="item.material === 'Al'"
                  class="text-xs bg-gray-200 text-gray-700 px-2 py-0.5 rounded border border-gray-300 ml-1">铝</span>
              </div>
              <div class="text-xs text-gray-400 mt-1 truncate max-w-[150px]" :title="item.remark">{{ item.remark }}
              </div>
            </td>

            <td class="px-6 py-4 text-sm">
              <div class="text-gray-400 text-xs mb-0.5">{{ item.material === 'Al' ? '铝' : '铜' }}价:</div>
              <div class="font-mono font-bold text-gray-700">${{ item.copper_price }}<span
                  class="text-xs font-normal text-gray-400">/kg</span></div>
            </td>

            <td class="px-6 py-4">
              <div class="text-xs text-gray-400 mb-0.5">Total Cost</div>
              <div class="text-lg font-bold text-gray-700">${{ item.total_cost }}</div>
            </td>

            <td class="px-6 py-4 bg-yellow-50 border-l border-yellow-100">
              <div class="text-xs text-yellow-600 mb-0.5">建议零售价</div>
              <div class="text-xl font-black text-yellow-600">${{ item.reference_price }}</div>
            </td>

            <td class="px-6 py-4">
              <span v-if="item.is_converted"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                ✅ 已发布
              </span>
              <span v-else
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                未发布
              </span>
            </td>

            <td class="px-6 py-4 text-right text-sm font-medium space-x-3">
              <button v-if="!item.is_converted" @click="openConvert(item)"
                class="text-green-600 hover:text-green-900 font-bold">
                🚀 转商品
              </button>
              <button @click="openEdit(item)" class="text-indigo-600 hover:text-indigo-900">编辑</button>
              <button @click="handleDelete(item.id)" class="text-red-600 hover:text-red-900">删除</button>
            </td>
          </tr>
          <tr v-if="list.length === 0">
            <td colspan="6" class="px-6 py-10 text-center text-gray-400">暂无数据，请先新建或刷新</td>
          </tr>
        </tbody>
      </table>
    </div>

    <CostCalculatorModal :is-open="showModal" :edit-data="currentEditItem" @close="showModal = false"
      @saved="handleSaved" />

    <div v-if="showConvertModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white p-6 rounded-lg w-[500px] shadow-2xl">
        <h2 class="text-xl font-bold mb-4 text-indigo-700">🚀 发布商品</h2>
        <div class="space-y-4">
          <div><label class="lbl">商品名称 (前台显示)</label><input v-model="convertForm.name" class="input-std font-bold">
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div><label class="lbl">销售价格 ($)</label><input v-model.number="convertForm.price" type="number"
                class="input-std text-yellow-600"></div>
            <div><label class="lbl">目标分类</label>
              <select v-model="convertForm.target_category_id" class="input-std">
                <option :value="null">-- 请选择 --</option>
                <option v-for="cat in flatCategories" :key="cat.id" :value="cat.id">{{ '|-- '.repeat(cat.level) +
                  cat.name }}</option>
              </select>
            </div>
          </div>
          <div><label class="lbl">图片链接 (可选)</label><input v-model="convertForm.image_url" class="input-std"
              placeholder="/static/uploads/..."></div>
          <div><label class="lbl">描述</label><textarea v-model="convertForm.description" rows="3"
              class="input-std"></textarea></div>
        </div>
        <div class="flex justify-end gap-3 mt-6 pt-4 border-t">
          <button @click="showConvertModal = false" class="px-4 py-2 text-gray-500 hover:text-gray-700">取消</button>
          <button @click="handleConvert"
            class="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded font-bold shadow">确认发布</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue';
import axios from '../../api/axios';
import CostCalculatorModal from '@/components/admin/CostCalculatorModal.vue';

// 基础数据
const list = ref([]);
const categoryOptions = ref([]);
const filterCategory = ref('');
const searchQuery = ref('');
const syncing = ref(false);
const currentMarketPrice = ref(0);
const currentRate = ref(0);

// 编辑/新建相关
const showModal = ref(false);
const currentEditItem = ref(null);

// 转商品相关
const showConvertModal = ref(false);
const treeData = ref([]); // 分类树
const convertForm = reactive({ cost_id: null, name: '', price: 0, target_category_id: null, description: '', image_url: '' });

// API 调用
const fetchCategories = async () => {
  try {
    const res = await axios.get('/admin/costs/categories');
    categoryOptions.value = res.data;
  } catch (e) { console.error(e); }
};

const fetchData = async () => {
  try {
    const params = {};
    if (filterCategory.value) params.category = filterCategory.value;
    if (searchQuery.value) params.search = searchQuery.value;
    const res = await axios.get('/admin/costs/', { params });
    list.value = res.data;
  } catch (e) { console.error(e); }
};

const fetchCategoryTree = async () => {
  try {
    const res = await axios.get('/products/categories/tree');
    treeData.value = res.data;
  } catch (e) { console.error(e); }
};

const flatten = (nodes, level = 0) => {
  let res = [];
  for (const node of nodes) {
    res.push({ ...node, level });
    if (node.children) res = res.concat(flatten(node.children, level + 1));
  }
  return res;
};
const flatCategories = computed(() => flatten(treeData.value));

// Actions
const syncPrices = async () => {
  if (!confirm("⚠️ 确定要操作吗？\n\n系统将获取今日最新 [市场铜价]，并重新计算所有产品的成本与售价")) return;
  syncing.value = true;
  try {
    const res = await axios.post('/admin/costs/sync-market-prices');
    alert(`✅ 同步成功！\n${res.data.message}`);
    currentMarketPrice.value = res.data.market_cny;
    currentRate.value = res.data.rate;
    await fetchData();
  } catch (e) { alert("❌ 同步失败"); } finally { syncing.value = false; }
};

const handleSaved = () => { fetchData(); fetchCategories(); };
const openCreate = () => { currentEditItem.value = null; showModal.value = true; };
const openEdit = (item) => { currentEditItem.value = { ...item }; showModal.value = true; };
const handleDelete = async (id) => { if (confirm("确定删除？")) { await axios.delete(`/admin/costs/${id}`); handleSaved(); } };

// Convert Actions
const openConvert = (item) => {
  fetchCategoryTree(); // 确保分类树加载
  convertForm.cost_id = item.id;
  convertForm.name = item.spec_name;
  convertForm.price = item.reference_price;
  convertForm.description = `Professional Cable: ${item.spec_name} (${item.category || 'Standard'})`;
  convertForm.target_category_id = null;
  convertForm.image_url = '';
  showConvertModal.value = true;
};

const handleConvert = async () => {
  if (!convertForm.target_category_id) return alert("请选择目标分类");
  try {
    await axios.post('/products/convert-from-cost', convertForm);
    alert("✅ 发布成功！");
    showConvertModal.value = false;
    fetchData(); // 刷新状态
  } catch (e) {
    alert("发布失败: " + (e.response?.data?.detail || e.message));
  }
};

onMounted(() => { fetchData(); fetchCategories(); });
</script>

<style scoped>
.th-std {
  @apply px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider;
}

.input-std {
  @apply w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none;
}

.lbl {
  @apply block text-xs font-bold text-gray-500 mb-1;
}

/* 2. 强制所有表格单元格垂直居中 */
:deep(td),
:deep(th) {
  vertical-align: middle !important;
}
</style>