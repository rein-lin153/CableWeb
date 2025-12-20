<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-800">📦 商品发布中心</h1>
      <p class="text-sm text-gray-500">基于 [成本核算] 数据直接生成前台商品</p>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="th-std">成本来源 (规格)</th>
            <th class="th-std">核算分类</th>
            <th class="th-std">建议零售价</th>
            <th class="th-std">前台状态</th>
            <th class="th-std text-right">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="item in costList" :key="item.id" class="hover:bg-gray-50">
            <td class="px-6 py-4">
              <div class="font-bold text-gray-900">{{ item.spec_name }}</div>
              <div class="text-xs text-gray-400">{{ item.remark }}</div>
            </td>
            <td class="px-6 py-4 text-sm text-gray-600">
              <span class="bg-gray-100 px-2 py-1 rounded">{{ item.category }}</span>
            </td>
            <td class="px-6 py-4">
              <div class="text-lg font-bold text-yellow-600">${{ item.reference_price }}</div>
            </td>
            <td class="px-6 py-4">
              <span class="text-xs text-gray-400">待发布</span> 
            </td>
            <td class="px-6 py-4 text-right">
              <button 
                @click="openConvert(item)" 
                class="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded text-xs shadow transition flex items-center gap-1 ml-auto"
              >
                🚀 转为商品
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white p-6 rounded-lg w-[500px] shadow-2xl">
        <h2 class="text-xl font-bold mb-4 text-indigo-700">🚀 发布商品</h2>
        
        <div class="space-y-4">
          <div>
            <label class="lbl">商品名称 (前台显示)</label>
            <input v-model="form.name" class="input-std font-bold">
          </div>
          
          <div class="grid grid-cols-2 gap-4">
             <div>
               <label class="lbl">销售价格 ($)</label>
               <input v-model.number="form.price" type="number" class="input-std text-yellow-600">
             </div>
             <div>
               <label class="lbl">目标分类</label>
               <select v-model="form.target_category_id" class="input-std">
                 <option :value="null">-- 请选择 --</option>
                 <option v-for="cat in flatCategories" :key="cat.id" :value="cat.id">
                   {{ '|-- '.repeat(cat.level) + cat.name }}
                 </option>
               </select>
             </div>
          </div>

          <div>
            <label class="lbl">图片链接 (可选)</label>
            <input v-model="form.image_url" class="input-std" placeholder="/static/uploads/...">
          </div>
          
          <div>
            <label class="lbl">描述</label>
            <textarea v-model="form.description" rows="3" class="input-std"></textarea>
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-6 pt-4 border-t">
          <button @click="showModal=false" class="px-4 py-2 text-gray-500 hover:text-gray-700">取消</button>
          <button @click="handleConvert" class="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded font-bold shadow">
            确认发布
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue';
import axios from '../../api/axios';

const costList = ref([]);
const treeData = ref([]);
const showModal = ref(false);

const form = reactive({
  cost_id: null,
  name: '',
  price: 0,
  target_category_id: null,
  description: '',
  image_url: ''
});

// 拉取成本列表
const fetchCosts = async () => {
  const res = await axios.get('/admin/costs/');
  costList.value = res.data;
};

// 拉取分类树(用于下拉选择)
const fetchCategories = async () => {
  const res = await axios.get('/products/categories/tree');
  treeData.value = res.data;
};

// 扁平化分类树
const flatten = (nodes, level = 0) => {
  let res = [];
  for (const node of nodes) {
    res.push({ ...node, level });
    if (node.children) res = res.concat(flatten(node.children, level + 1));
  }
  return res;
};
const flatCategories = computed(() => flatten(treeData.value));

const openConvert = (item) => {
  form.cost_id = item.id;
  form.name = item.spec_name; // 默认使用规格名
  form.price = item.reference_price; // 默认使用参考价
  form.description = `Professional Cable: ${item.spec_name} (${item.category})`;
  form.target_category_id = null;
  showModal.value = true;
};

const handleConvert = async () => {
  if(!form.target_category_id) return alert("请选择目标分类");
  try {
    await axios.post('/products/convert-from-cost', form);
    alert("✅ 发布成功！该商品已上线。");
    showModal.value = false;
  } catch (e) {
    alert("发布失败: " + (e.response?.data?.detail || e.message));
  }
};

onMounted(() => {
  fetchCosts();
  fetchCategories();
});
</script>

<style scoped>
.th-std { @apply px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase; }
.input-std { @apply w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none; }
.lbl { @apply block text-xs font-bold text-gray-500 mb-1; }
</style>