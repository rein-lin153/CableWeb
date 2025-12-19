<template>
  <div class="flex flex-col h-full bg-white rounded-xl shadow-sm border border-gray-100">

    <div
      class="p-4 md:p-6 border-b border-gray-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <h2 class="text-xl font-bold text-gray-900 flex items-center">
        <span class="w-2 h-6 bg-orange-500 rounded-full mr-3"></span>
        产品库存与SKU管理
      </h2>
      <div class="flex w-full sm:w-auto space-x-2">
        <div class="flex-1 max-w-sm mx-4"> <input v-model="searchQuery" @keyup.enter="fetchData" type="text"
            placeholder="搜索产品名称..."
            class="w-full px-4 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-orange-500 outline-none">
        </div>
        <button @click="$router.push('/admin/categories')"
          class="flex-1 sm:flex-none bg-white border border-gray-300 text-gray-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center justify-center">
          <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          分类
        </button>
        <button @click="openCreateModal"
          class="flex-1 sm:flex-none bg-gray-900 text-white px-3 py-2 rounded-lg text-sm font-medium hover:bg-orange-600 transition-colors flex items-center justify-center">
          <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          新增产品
        </button>
      </div>
    </div>

    <div class="flex-1 overflow-auto">
      <table class="hidden md:table min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50 sticky top-0 z-10">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">产品图</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">名称 / 描述</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">分类</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">价格区间</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">总库存</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-if="loading">
            <td colspan="6" class="p-10 text-center text-gray-500">加载中...</td>
          </tr>
          <tr v-else v-for="product in products" :key="product.id" class="hover:bg-gray-50 transition-colors">
            <td class="px-6 py-4 whitespace-nowrap">
              <img :src="product.image_url" class="h-12 w-12 object-cover rounded bg-gray-100 border border-gray-200">
            </td>
            <td class="px-6 py-4">
              <div class="text-sm font-bold text-gray-900">{{ product.name }}</div>
              <div class="text-xs text-gray-500 truncate w-48">{{ product.description }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-600">
                {{ getCategoryName(product.category_id) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap font-mono text-sm text-orange-600 font-bold">
              {{ getPriceRange(product.variants) }}
              <span class="text-xs text-gray-400 font-normal">/ {{ product.unit || '单位' }}</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm font-bold"
                :class="getTotalStock(product.variants) > 0 ? 'text-green-600' : 'text-red-500'">
                {{ getTotalStock(product.variants) }}
                <span class="font-normal text-gray-400 text-xs">{{ product.unit || '件' }}</span>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-3">
              <button @click="openEditModal(product)" class="text-indigo-600 hover:text-indigo-900">编辑SKU</button>
              <button @click="handleDelete(product)" class="text-red-600 hover:text-red-900">删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="md:hidden p-4 space-y-4">
        <div v-if="loading" class="text-center py-10 text-gray-400">加载中...</div>
        <div v-for="product in products" :key="product.id"
          class="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
          <div class="flex items-start">
            <img :src="product.image_url" class="h-16 w-16 object-cover rounded-lg border">
            <div class="ml-4 flex-1 min-w-0">
              <div class="flex justify-between items-start">
                <span class="text-[10px] bg-gray-100 px-2 py-0.5 rounded text-gray-500 uppercase font-bold">{{
                  getCategoryName(product.category_id) }}</span>
                <div class="text-sm font-black text-orange-600">{{ getPriceRange(product.variants) }}</div>
              </div>
              <h3 class="font-bold text-gray-900 truncate mt-1">{{ product.name }}</h3>
              <p class="text-xs text-gray-400 truncate">{{ product.description }}</p>
            </div>
          </div>
          <div class="mt-4 pt-3 border-t border-gray-50 flex justify-between items-center">
            <div class="text-xs">
              库存: <span class="font-bold"
                :class="getTotalStock(product.variants) > 0 ? 'text-green-600' : 'text-red-500'">{{
                  getTotalStock(product.variants) }}</span> {{ product.unit }}
            </div>
            <div class="space-x-4">
              <button @click="openEditModal(product)" class="text-sm font-bold text-indigo-600">编辑</button>
              <button @click="handleDelete(product)" class="text-sm font-bold text-red-500">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-2 sm:p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[95vh] flex flex-col overflow-hidden">

        <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
          <h3 class="text-lg font-bold text-gray-900">{{ editingId ? '编辑产品 & SKU' : '新增产品' }}</h3>
          <button @click="showModal = false" class="text-gray-400 hover:text-gray-600">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
            <div class="col-span-1 md:col-span-2">
              <label class="block text-sm font-bold text-gray-700 mb-1">产品名称</label>
              <input v-model="form.name" type="text"
                class="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-orange-500 outline-none">
            </div>

            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1">所属分类</label>
              <select v-model="form.category_id"
                class="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-orange-500 outline-none bg-white">
                <option :value="null">请选择分类</option>
                <option v-for="cat in categoryOptions" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1">计价单位</label>
              <input v-model="form.unit" type="text"
                class="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-orange-500 outline-none">
            </div>

            <div class="col-span-1 md:col-span-2">
              <label class="block text-sm font-bold text-gray-700 mb-1">图片 URL</label>
              <input v-model="form.image_url" type="text"
                class="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-orange-500 outline-none">
            </div>
          </div>

          <div>
            <div class="flex justify-between items-center mb-3">
              <h4 class="text-base font-bold text-gray-900">规格配置 (SKU)</h4>
              <button @click="addVariant"
                class="text-xs bg-blue-50 text-blue-600 px-3 py-1.5 rounded-lg font-bold border border-blue-200">
                + 添加规格
              </button>
            </div>

            <div class="border border-gray-200 rounded-xl overflow-x-auto">
              <table class="min-w-[600px] md:min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">规格 (平方)</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">颜色</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">单价 (¥)</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">库存</th>
                    <th class="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase w-16">操作</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200 bg-white">
                  <tr v-for="(variant, index) in form.variants" :key="index">
                    <td class="px-2 py-2"><input v-model="variant.spec" type="text"
                        class="w-full border-gray-200 rounded text-sm"></td>
                    <td class="px-2 py-2"><input v-model="variant.color" type="text"
                        class="w-full border-gray-200 rounded text-sm"></td>
                    <td class="px-2 py-2"><input v-model.number="variant.price" type="number" step="0.01"
                        class="w-full border-gray-200 rounded text-sm"></td>
                    <td class="px-2 py-2"><input v-model.number="variant.stock" type="number"
                        class="w-full border-gray-200 rounded text-sm"></td>
                    <td class="px-2 py-2 text-center">
                      <button @click="removeVariant(index)" class="text-red-400 p-1"><svg class="w-5 h-5" fill="none"
                          viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg></button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="p-4 md:p-6 border-t border-gray-100 bg-gray-50 flex flex-col-reverse sm:flex-row justify-end gap-3">
          <button @click="showModal = false"
            class="w-full sm:w-auto px-5 py-2.5 text-gray-600 hover:bg-gray-200 rounded-lg text-sm font-medium">取消</button>
          <button @click="handleSubmit" :disabled="submitting"
            class="w-full sm:w-auto px-5 py-2.5 bg-gray-900 text-white rounded-lg hover:bg-orange-600 text-sm font-medium disabled:opacity-50">
            {{ editingId ? '保存修改' : '确认创建' }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import api from '../../api/axios';

const products = ref([]);
const categories = ref([]);
const loading = ref(false);
const showModal = ref(false);
const submitting = ref(false);
const editingId = ref(null);

const form = reactive({
  name: '',
  category_id: null,
  unit: '卷',
  image_url: '',
  description: '',
  variants: []
});

const searchQuery = ref(''); // 1. 新增变量

const fetchData = async () => {
  loading.value = true;
  try {
    const [prodRes, catRes] = await Promise.all([
      // 2. 修改 API 调用，传入 q 参数
      api.get('/products/', { params: { q: searchQuery.value || undefined } }),
      api.get('/categories/?flat=true')
    ]);
    products.value = prodRes.data;
    categories.value = catRes.data;
  } catch (error) { 
    console.error(error); 
  } finally { 
    loading.value = false; 
  }
};

const categoryOptions = computed(() => {
  const buildTree = (items, parentId = null, level = 0) => {
    return items
      .filter(item => item.parent_id === parentId)
      .map(item => ({
        ...item,
        level,
        children: buildTree(items, item.id, level + 1)
      }));
  };

  const flattenTree = (tree) => {
    let result = [];
    for (const node of tree) {
      result.push(node);
      if (node.children) result = result.concat(flattenTree(node.children));
    }
    return result;
  };

  if (!categories.value.length) return [];
  const tree = buildTree(categories.value);
  const flat = flattenTree(tree);

  return flat.map(cat => ({
    id: cat.id,
    name: '　'.repeat(cat.level) + (cat.level > 0 ? '└ ' : '') + cat.name
  }));
});

const getCategoryName = (id) => categories.value.find(c => c.id === id)?.name || '未分类';

const getPriceRange = (variants) => {
  if (!variants || variants.length === 0) return '暂无报价';
  const prices = variants.map(v => v.price);
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  if (min === max) return `¥${min}`;
  return `¥${min} - ¥${max}`;
};

const getTotalStock = (variants) => {
  if (!variants) return 0;
  return variants.reduce((sum, v) => sum + v.stock, 0);
};

const openCreateModal = () => {
  editingId.value = null;
  Object.assign(form, { name: '', category_id: null, unit: '卷', image_url: '', description: '', variants: [] });
  form.variants.push({ spec: '', color: '', price: 0, stock: 0 });
  showModal.value = true;
};

const openEditModal = (product) => {
  editingId.value = product.id;
  Object.assign(form, {
    name: product.name,
    category_id: product.category_id,
    unit: product.unit || '卷',
    image_url: product.image_url,
    description: product.description,
    variants: JSON.parse(JSON.stringify(product.variants || []))
  });
  showModal.value = true;
};

const addVariant = () => { form.variants.push({ spec: '', color: '', price: 0, stock: 0 }); };
const removeVariant = (index) => { form.variants.splice(index, 1); };

const handleSubmit = async () => {
  if (!form.name || !form.category_id) return alert("请填写基本信息");
  if (form.variants.length === 0) return alert("请至少添加一种规格");
  submitting.value = true;
  try {
    if (editingId.value) {
      await api.put(`/products/${editingId.value}`, form);
    } else {
      await api.post('/products/', form);
    }
    showModal.value = false;
    fetchData();
  } catch (e) {
    alert("操作失败：" + (e.response?.data?.detail || "未知错误"));
  } finally {
    submitting.value = false;
  }
};

const handleDelete = async (product) => {
  if (!confirm(`确定删除 ${product.name} 及其所有规格吗？`)) return;
  try {
    await api.delete(`/products/${product.id}`);
    fetchData();
  } catch (e) { alert("删除失败"); }
};

onMounted(fetchData);
</script>

<style scoped>
/* 隐藏移动端滚动条 */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>