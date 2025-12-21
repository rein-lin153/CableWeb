<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    <div class="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
          📦 商品管理
          <span v-if="loading" class="text-sm font-normal text-gray-400 animate-pulse">加载中...</span>
        </h1>
        <p class="text-sm text-gray-500 mt-1">管理已上架商品、编辑变体与库存</p>
      </div>
      
      <div class="flex gap-3">
        <div class="relative">
          <input 
            v-model="searchQuery"
            type="text" 
            placeholder="搜索商品名称或分类..." 
            class="pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 w-64 shadow-sm"
          >
          <svg class="w-4 h-4 text-gray-400 absolute left-3 top-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
        </div>

        <button @click="fetchProducts" 
          class="bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm flex items-center gap-2">
          <svg class="w-4 h-4" :class="{'animate-spin': loading}" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
          刷新
        </button>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">商品名称</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">分类</th>
              <th scope="col" class="px-6 py-3 text-center text-xs font-bold text-gray-500 uppercase tracking-wider">变体数</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">总库存</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">基准价格</th>
              <th scope="col" class="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 bg-white">
            <tr v-for="p in filteredProducts" :key="p.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="h-10 w-10 flex-shrink-0">
                    <img v-if="p.image_url" :src="p.image_url" class="h-10 w-10 rounded-lg object-cover border border-gray-200" alt="">
                    <div v-else class="h-10 w-10 rounded-lg bg-gray-100 flex items-center justify-center text-gray-400 text-xs">无图</div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-bold text-gray-900">{{ p.name }}</div>
                    <div class="text-xs text-gray-500 truncate max-w-[12rem]">{{ p.description }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-600">
                  {{ p.category_detail?.name || '未分类' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span class="text-sm text-gray-600 font-mono bg-blue-50 text-blue-700 px-2 py-0.5 rounded border border-blue-100">
                  {{ p.variants.length }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <div class="flex items-center font-medium" :class="getTotalStock(p) > 100 ? 'text-green-600' : 'text-orange-600'">
                  <span class="w-2 h-2 rounded-full mr-2" :class="getTotalStock(p) > 100 ? 'bg-green-500' : 'bg-orange-500'"></span>
                  {{ getTotalStock(p) }} {{ p.unit }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                ${{ p.price }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button @click="openEdit(p)" class="text-indigo-600 hover:text-indigo-900 bg-indigo-50 hover:bg-indigo-100 px-3 py-1.5 rounded-md transition-colors">
                  编辑
                </button>
              </td>
            </tr>
            <tr v-if="filteredProducts.length === 0">
              <td colspan="6" class="px-6 py-10 text-center text-gray-400">
                <div class="flex flex-col items-center">
                  <svg class="w-12 h-12 text-gray-300 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" /></svg>
                  <p>未找到匹配商品</p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="!saving && (showModal = false)"></div>

        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <div class="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="flex justify-between items-start mb-5">
              <div>
                <h3 class="text-xl leading-6 font-bold text-gray-900" id="modal-title">编辑商品详情</h3>
                <p class="text-sm text-gray-500 mt-1">ID: {{ currentId }}</p>
              </div>
              <button @click="showModal = false" :disabled="saving" class="bg-gray-100 rounded-full p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-200 focus:outline-none">
                <span class="sr-only">Close</span>
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>

            <div class="space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-4">
                   <div>
                     <label class="lbl">商品名称</label>
                     <input v-model="form.name" class="input-std" placeholder="例如：BV 2.5mm² 电线">
                   </div>
                   <div class="grid grid-cols-2 gap-4">
                     <div>
                       <label class="lbl">基准价格 ($)</label>
                       <input v-model.number="form.price" type="number" step="0.01" class="input-std">
                     </div>
                     <div>
                       <label class="lbl">计量单位</label>
                       <input v-model="form.unit" class="input-std" placeholder="例如：卷">
                     </div>
                   </div>
                </div>
                
                <div class="space-y-4">
                   <div>
                     <label class="lbl">图片链接 URL</label>
                     <input v-model="form.image_url" class="input-std" placeholder="https://...">
                   </div>
                   <div>
                     <label class="lbl">商品描述</label>
                     <textarea v-model="form.description" rows="3" class="input-std resize-none"></textarea>
                   </div>
                </div>
              </div>

              <div class="border-t border-gray-100 pt-6">
                <div class="flex justify-between items-center mb-4">
                  <h4 class="text-lg font-bold text-gray-800 flex items-center">
                    <span class="bg-indigo-100 text-indigo-600 p-1.5 rounded-lg mr-2">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" /></svg>
                    </span>
                    规格与库存管理
                  </h4>
                  <button @click="addVariant" class="text-sm bg-indigo-50 text-indigo-700 px-3 py-1.5 rounded-lg hover:bg-indigo-100 font-medium transition-colors border border-indigo-200 flex items-center">
                    <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
                    添加规格
                  </button>
                </div>

                <div class="bg-gray-50 rounded-xl border border-gray-200 overflow-hidden">
                  <table class="w-full text-sm">
                    <thead class="bg-gray-100 border-b border-gray-200">
                      <tr>
                        <th class="px-4 py-2 text-left font-semibold text-gray-600">规格型号</th>
                        <th class="px-4 py-2 text-left font-semibold text-gray-600">颜色/属性</th>
                        <th class="px-4 py-2 text-left font-semibold text-gray-600">单价 ($)</th>
                        <th class="px-4 py-2 text-left font-semibold text-gray-600">库存数量</th>
                        <th class="px-4 py-2 text-center font-semibold text-gray-600 w-16">操作</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                      <tr v-for="(v, idx) in form.variants" :key="idx" class="group bg-white hover:bg-gray-50">
                        <td class="p-2">
                          <input v-model="v.spec" class="w-full bg-transparent border-b border-transparent focus:border-indigo-500 focus:outline-none py-1 transition-colors" placeholder="规格">
                        </td>
                        <td class="p-2">
                          <input v-model="v.color" class="w-full bg-transparent border-b border-transparent focus:border-indigo-500 focus:outline-none py-1 transition-colors" placeholder="颜色">
                        </td>
                        <td class="p-2">
                          <input v-model.number="v.price" type="number" step="0.01" class="w-full bg-transparent border-b border-transparent focus:border-indigo-500 focus:outline-none py-1 transition-colors font-mono">
                        </td>
                        <td class="p-2">
                          <input v-model.number="v.stock" type="number" class="w-full bg-transparent border-b border-transparent focus:border-indigo-500 focus:outline-none py-1 transition-colors font-bold text-indigo-600">
                        </td>
                        <td class="p-2 text-center">
                          <button @click="removeVariant(idx)" class="text-gray-400 hover:text-red-500 p-1 rounded-full hover:bg-red-50 transition-colors" title="移除">
                            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                          </button>
                        </td>
                      </tr>
                      <tr v-if="form.variants.length === 0">
                        <td colspan="5" class="p-4 text-center text-gray-400 text-xs">
                          暂无变体，请点击上方按钮添加
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse border-t border-gray-200">
            <button @click="handleSave" :disabled="saving"
              class="w-full inline-flex justify-center rounded-lg border border-transparent shadow-sm px-5 py-2.5 bg-indigo-600 text-base font-bold text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-all items-center">
              <svg v-if="saving" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              {{ saving ? '正在保存...' : '保存修改' }}
            </button>
            <button @click="showModal = false" :disabled="saving"
              class="mt-3 w-full inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-5 py-2.5 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">
              取消
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue';
import axios from '../../api/axios'; // 确保路径正确，或使用 @/api/axios
import { useToast } from '../../composables/useToast'; // 引入 Toast

const { success, error: showError } = useToast();

const products = ref([]);
const loading = ref(false);
const saving = ref(false);
const showModal = ref(false);
const currentId = ref(null);
const searchQuery = ref('');

// 表单数据
const form = reactive({
  name: '', 
  description: '', 
  price: 0, 
  image_url: '', 
  unit: '卷',
  variants: []
});

const fetchProducts = async () => {
  loading.value = true;
  try {
    const res = await axios.get('/products/');
    products.value = res.data;
  } catch (e) {
    console.error(e);
    showError('无法加载商品列表');
  } finally {
    loading.value = false;
  }
};

// 前端过滤搜索
const filteredProducts = computed(() => {
  if (!searchQuery.value) return products.value;
  const q = searchQuery.value.toLowerCase();
  return products.value.filter(p => 
    p.name.toLowerCase().includes(q) || 
    (p.category_detail?.name || '').toLowerCase().includes(q)
  );
});

// 计算总库存
const getTotalStock = (p) => {
  return p.variants?.reduce((acc, v) => acc + (v.stock || 0), 0) || 0;
};

const openEdit = (p) => {
  currentId.value = p.id;
  form.name = p.name;
  form.description = p.description;
  form.price = p.price;
  form.image_url = p.image_url;
  form.unit = p.unit;
  // 深拷贝变体
  form.variants = p.variants ? p.variants.map(v => ({ ...v })) : [];
  showModal.value = true;
};

const addVariant = () => {
  form.variants.push({
    spec: form.name.split(' ')[0] || '规格', 
    color: 'Red',
    price: form.price,
    stock: 100,
    unit: form.unit,
    sku_code: '',
    copper_weight: 0, 
    process_cost: 0
  });
};

const removeVariant = (idx) => {
  // 如果是已存在的变体，这里建议加上确认，或者标记为删除等待后端处理
  // 但对于简单逻辑，直接移除即可
  if(confirm('确定要删除这个规格吗？此操作在保存后生效。')) {
    form.variants.splice(idx, 1);
  }
};

const handleSave = async () => {
  saving.value = true;
  try {
    // 确保所有数字字段是数字类型
    const payload = {
      ...form,
      price: Number(form.price),
      variants: form.variants.map(v => ({
        ...v,
        price: Number(v.price),
        stock: Number(v.stock)
      }))
    };
    
    await axios.put(`/products/${currentId.value}`, payload);
    success("保存成功！");
    showModal.value = false;
    await fetchProducts(); // 刷新列表
  } catch (e) {
    console.error(e);
    showError("保存失败: " + (e.response?.data?.detail || e.message));
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  fetchProducts();
});
</script>

<style scoped>
.lbl {
  @apply block text-xs font-bold text-gray-700 mb-1.5 uppercase tracking-wide;
}

.input-std {
  @apply block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border transition-all duration-200;
}

/* 移除默认的数字输入框箭头 */
input[type=number]::-webkit-inner-spin-button, 
input[type=number]::-webkit-outer-spin-button { 
  -webkit-appearance: none; 
  margin: 0; 
}
input[type=number] {
  -moz-appearance: textfield;
}
</style>