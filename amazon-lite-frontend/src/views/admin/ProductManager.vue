<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    <div class="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
          📦 商品与库存中心
          <span v-if="loading" class="text-sm font-normal text-gray-400 animate-pulse">加载中...</span>
        </h1>
        <p class="text-sm text-gray-500 mt-1">一站式管理商品信息、SKU 变体、库存数量与批发价格</p>
      </div>
      
      <div class="flex gap-3">
        <input 
          v-model="searchQuery"
          type="text" 
          placeholder="搜索商品 / 型号 / 规格..." 
          class="pl-4 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 w-64 shadow-sm outline-none transition-all"
        >
        <button @click="fetchProducts" 
          class="bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
          刷新
        </button>
        <button @click="openCreate" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-bold shadow-md transition-colors flex items-center gap-2">
          + 新建商品
        </button>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="th-std pl-6">商品信息</th>
            <th class="th-std">所属分类</th>
            <th class="th-std text-center">SKU数</th>
            <th class="th-std">总库存 (现货+在途)</th>
            <th class="th-std">基准售价</th>
            <th class="th-std text-right pr-6">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 bg-white">
          <tr v-for="p in filteredProducts" :key="p.id" class="hover:bg-gray-50 transition-colors group">
            <td class="px-6 py-4">
              <div class="flex items-center">
                <div class="h-12 w-12 flex-shrink-0 relative bg-gray-100 rounded-lg overflow-hidden border border-gray-200">
                  <img v-if="p.image_url" :src="p.image_url" class="h-full w-full object-cover mix-blend-multiply">
                  <div v-else class="h-full w-full flex items-center justify-center text-gray-400 text-xs">无图</div>
                </div>
                <div class="ml-4">
                  <div class="text-sm font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">{{ p.name }}</div>
                  <div class="text-xs text-gray-500 truncate max-w-[12rem] mt-0.5">{{ p.description || '暂无描述' }}</div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="px-2.5 py-1 inline-flex text-xs font-medium rounded-full bg-gray-100 text-gray-600 border border-gray-200">
                {{ p.category_detail?.name || '未分类' }}
              </span>
            </td>
            <td class="px-6 py-4 text-center">
              <span class="text-xs font-bold text-gray-500 bg-gray-100 px-2 py-1 rounded">{{ p.variants.length }} 色</span>
            </td>
            <td class="px-6 py-4 text-sm">
              <div class="flex flex-col">
                <div class="flex items-center font-bold" :class="getTotalStock(p) > 100 ? 'text-green-600' : 'text-orange-600'">
                  <span class="w-2 h-2 rounded-full mr-2" :class="getTotalStock(p) > 100 ? 'bg-green-500' : 'bg-orange-500'"></span>
                  {{ getTotalStock(p) }} {{ p.unit }}
                </div>
                <div v-if="getTotalIncoming(p) > 0" class="text-xs text-blue-500 pl-4 mt-0.5">
                  + {{ getTotalIncoming(p) }} 在途
                </div>
              </div>
            </td>
            <td class="px-6 py-4 text-sm font-mono font-medium text-gray-700">
              ¥{{ p.price }}
            </td>
            <td class="px-6 py-4 text-right text-sm font-medium space-x-2">
              <button @click="openEdit(p)" class="text-indigo-600 hover:text-indigo-900 bg-indigo-50 hover:bg-indigo-100 px-3 py-1.5 rounded-lg transition-colors font-bold">
                管理库存
              </button>
              <button @click="deleteProduct(p.id)" class="text-gray-400 hover:text-red-600 px-2 py-1.5 transition-colors" title="删除商品">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
              </button>
            </td>
          </tr>
          <tr v-if="filteredProducts.length === 0">
             <td colspan="6" class="px-6 py-12 text-center text-gray-400">
               没有找到商品，请尝试新建
             </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-center justify-center min-h-screen px-4 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="!saving && (showModal = false)"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <div class="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-5xl sm:w-full">
          <div class="bg-white px-6 pt-6 pb-4">
            <div class="flex justify-between items-start mb-6 border-b border-gray-100 pb-4">
              <div>
                <h3 class="text-xl font-bold text-gray-900">{{ currentId ? '编辑商品' : '新建商品' }}</h3>
                <p class="text-sm text-gray-500 mt-1">配置基本信息、分类与多色变体库存</p>
              </div>
              <button @click="showModal = false" class="bg-gray-100 hover:bg-gray-200 rounded-full p-2 text-gray-500 transition-colors">✕</button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
              <div class="col-span-1 space-y-5">
                 <div>
                   <label class="lbl">商品名称</label>
                   <input v-model="form.name" class="input-std font-bold text-gray-900" placeholder="如: BV 2.5平方">
                 </div>
                 
                 <div>
                   <label class="lbl flex justify-between items-center">
                     所属分类
                     <button @click="openCategoryModal" class="text-xs text-indigo-600 hover:text-indigo-800 font-bold bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100 transition-colors">
                       ⚙️ 管理分类
                     </button>
                   </label>
                   <select v-model="form.category_id" class="input-std appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20width%3D%2220%22%20height%3D%2220%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cpath%20d%3D%22M5%206l5%205%205-5%22%20stroke%3D%22%239CA3AF%22%20stroke-width%3D%222%22%20fill%3D%22none%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%2F%3E%3C%2Fsvg%3E')] bg-no-repeat bg-right-2 bg-white">
                      <option :value="null" class="text-gray-400">-- 请选择层级分类 --</option>
                      <option v-for="c in flatCategories" :key="c.id" :value="c.id" :class="{'font-bold text-indigo-900': c.level === 0}">
                        {{ '&nbsp;&nbsp;'.repeat(c.level) + (c.level > 0 ? '└─ ' : '') + c.name }}
                      </option>
                   </select>
                 </div>

                 <div class="grid grid-cols-2 gap-3">
                   <div>
                     <label class="lbl">基准价格 (¥)</label>
                     <input v-model.number="form.price" type="number" step="0.01" class="input-std text-orange-600 font-bold">
                   </div>
                   <div>
                     <label class="lbl">计量单位</label>
                     <input v-model="form.unit" class="input-std" placeholder="卷/米">
                   </div>
                 </div>
                 <div>
                   <label class="lbl">封面图 URL</label>
                   <input v-model="form.image_url" class="input-std text-xs text-gray-500">
                 </div>
                 <div>
                   <label class="lbl">描述备注</label>
                   <textarea v-model="form.description" rows="3" class="input-std"></textarea>
                 </div>
              </div>
              
              <div class="col-span-2 flex flex-col h-full">
                
                <div class="bg-indigo-50 border border-indigo-100 rounded-xl p-4 mb-4">
                  <div class="flex justify-between items-center mb-2">
                    <span class="text-xs font-bold text-indigo-800 flex items-center">
                      <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                      一键生成标准 6 色 (红/兰/黄/绿/双/黑)
                    </span>
                  </div>
                  <div class="flex gap-2 items-end">
                    <div class="flex-1">
                      <label class="text-[10px] text-indigo-500 font-bold mb-1 block">统一规格名称</label>
                      <input v-model="batchSpec" placeholder="如: 2.5mm²" class="w-full text-xs border border-indigo-200 rounded px-2 py-1.5 focus:ring-2 focus:ring-indigo-500 outline-none">
                    </div>
                    <div class="w-20">
                      <label class="text-[10px] text-indigo-500 font-bold mb-1 block">单价</label>
                      <input v-model.number="batchPrice" type="number" class="w-full text-xs border border-indigo-200 rounded px-2 py-1.5 text-center font-bold">
                    </div>
                    <div class="w-20">
                      <label class="text-[10px] text-indigo-500 font-bold mb-1 block">初始库存</label>
                      <input v-model.number="batchStock" type="number" class="w-full text-xs border border-indigo-200 rounded px-2 py-1.5 text-center">
                    </div>
                    <button @click="addStandardColors" class="bg-indigo-600 hover:bg-indigo-700 text-white text-xs px-4 py-1.5 rounded font-bold shadow-md transition-colors h-[30px]">
                      ⚡ 立即生成
                    </button>
                  </div>
                </div>

                <div class="flex justify-between items-center mb-2">
                  <label class="lbl mb-0">SKU 列表 ({{ form.variants.length }})</label>
                  <button @click="addVariant" class="text-xs text-gray-500 hover:text-indigo-600 border border-gray-200 px-2 py-1 rounded hover:bg-gray-50">
                    + 添加单个空行
                  </button>
                </div>
                
                <div class="bg-white rounded-xl border border-gray-200 overflow-hidden flex-1 overflow-y-auto min-h-[300px] max-h-[500px]">
                  <table class="w-full text-xs relative">
                    <thead class="bg-gray-100 border-b border-gray-200 text-gray-500 sticky top-0 z-10">
                      <tr>
                        <th class="px-3 py-2 text-left bg-gray-100">规格/颜色</th>
                        <th class="px-3 py-2 text-left w-20 bg-gray-100">价格</th>
                        <th class="px-3 py-2 text-left w-20 bg-gray-100">现货</th>
                        <th class="px-3 py-2 text-left w-24 bg-blue-50/50 text-blue-600">在途 & 日期</th>
                        <th class="px-3 py-2 text-left w-32 bg-yellow-50/50 text-yellow-600">批发 (量/折)</th>
                        <th class="px-2 py-2 text-center w-10 bg-gray-100"></th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                      <tr v-for="(v, idx) in form.variants" :key="idx" class="bg-white hover:bg-gray-50 group">
                        <td class="p-2 align-top">
                          <input v-model="v.spec" class="w-full border-b border-gray-200 focus:border-indigo-500 outline-none bg-transparent mb-1 font-medium" placeholder="规格">
                          <input v-model="v.color" class="w-full border-b border-gray-200 focus:border-indigo-500 outline-none bg-transparent text-[10px] text-gray-500" placeholder="颜色">
                        </td>
                        <td class="p-2 align-top">
                          <input v-model.number="v.price" type="number" class="w-full border rounded px-1 py-1 text-center font-bold text-gray-700">
                        </td>
                        <td class="p-2 align-top">
                          <input v-model.number="v.stock" type="number" class="w-full border rounded px-1 py-1 text-center font-bold text-green-600 bg-green-50/30">
                        </td>
                        <td class="p-2 bg-blue-50/10 align-top space-y-1">
                          <input v-model.number="v.incoming_stock" type="number" class="w-full border border-blue-200 rounded px-1 py-0.5 text-center text-blue-600" placeholder="0">
                          <input v-model="v.arrival_date" type="text" class="w-full text-[10px] text-gray-400 bg-transparent text-center outline-none border-b border-transparent focus:border-blue-300" placeholder="如: 6月15日">
                        </td>
                        <td class="p-2 bg-yellow-50/10 align-top">
                          <div class="flex items-center gap-1 mb-1">
                            <span class="text-gray-400 text-[10px]">≥</span>
                            <input v-model.number="v.tier_min_qty" type="number" class="w-full border rounded px-0.5 py-0.5 text-center" placeholder="100">
                          </div>
                          <div class="flex items-center gap-1">
                            <span class="text-gray-400 text-[10px]">折</span>
                            <input v-model.number="v.tier_discount" type="number" step="0.01" class="w-full border rounded px-0.5 py-0.5 text-center text-yellow-600 font-bold" placeholder="0.98">
                          </div>
                        </td>
                        <td class="p-2 text-center align-middle">
                          <button @click="removeVariant(idx)" class="text-gray-300 hover:text-red-500 transition-colors text-lg">×</button>
                        </td>
                      </tr>
                      <tr v-if="form.variants.length === 0">
                        <td colspan="6" class="py-8 text-center text-gray-400 text-xs">
                          暂无变体，请点击上方按钮快速生成
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <div class="flex justify-end gap-3 pt-4 border-t border-gray-100">
              <button @click="showModal = false" class="px-5 py-2.5 rounded-lg border border-gray-300 text-gray-700 font-medium hover:bg-gray-50 transition-colors">取消</button>
              <button @click="handleSave" :disabled="saving" class="px-6 py-2.5 rounded-lg bg-indigo-600 text-white font-bold hover:bg-indigo-700 shadow-md disabled:opacity-50 flex items-center transition-all">
                <svg v-if="saving" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                保存所有配置
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showCategoryModal" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="bg-white rounded-xl shadow-2xl w-[600px] max-h-[80vh] flex flex-col animate-fade-in-up">
        
        <div class="p-5 border-b border-gray-100 flex justify-between items-center bg-gray-50 rounded-t-xl">
          <h3 class="text-lg font-bold text-gray-800">⚙️ 分类管理中心</h3>
          <button @click="showCategoryModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>

        <div class="flex flex-1 overflow-hidden">
          
          <div class="w-1/2 border-r border-gray-100 p-4 overflow-y-auto bg-gray-50/50">
            <h4 class="text-xs font-bold text-gray-500 mb-3 uppercase tracking-wider">已存在分类</h4>
            <ul class="space-y-1">
              <li v-if="flatCategories.length === 0" class="text-xs text-gray-400 text-center py-4">暂无分类</li>
              <li v-for="c in flatCategories" :key="c.id" class="flex justify-between items-center group p-2 hover:bg-white hover:shadow-sm rounded transition-all">
                <span class="text-sm text-gray-700" :class="{'font-bold text-indigo-900': c.level === 0}">
                  {{ '│ '.repeat(c.level) + (c.level > 0 ? '├ ' : '') + c.name }}
                </span>
                <button @click="deleteCategory(c.id)" class="text-gray-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity p-1" title="删除分类">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                </button>
              </li>
            </ul>
          </div>

          <div class="w-1/2 p-6 flex flex-col justify-center">
            <h4 class="text-sm font-bold text-gray-800 mb-4 flex items-center">
              <span class="w-6 h-6 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center mr-2 text-xs">+</span>
              添加新分类
            </h4>
            
            <div class="space-y-4">
              <div>
                <label class="lbl">分类名称</label>
                <input v-model="catForm.name" class="input-std" placeholder="如：低压电缆">
              </div>
              <div>
                <label class="lbl">上级分类 (可选)</label>
                <select v-model="catForm.parent_id" class="input-std">
                  <option :value="null">-- 设为顶级分类 --</option>
                  <option v-for="c in flatCategories" :key="c.id" :value="c.id">
                    {{ '&nbsp;&nbsp;'.repeat(c.level) + (c.level > 0 ? '└─ ' : '') + c.name }}
                  </option>
                </select>
              </div>
              <button @click="createCategory" class="w-full py-2.5 bg-indigo-600 text-white font-bold rounded-lg shadow-md hover:bg-indigo-700 transition-transform active:scale-95 text-sm mt-2">
                立即创建
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue';
import axios from '../../api/axios';
import { useToast } from '../../composables/useToast';

const { success, error: showError } = useToast();

const products = ref([]);
const rawCategories = ref([]); // 原始分类数据
const loading = ref(false);
const saving = ref(false);
const showModal = ref(false);
const currentId = ref(null);
const searchQuery = ref('');

// 批量生成器的临时变量
const batchSpec = ref('');
const batchPrice = ref(0);
const batchStock = ref(100);

// 分类管理小弹窗
const showCategoryModal = ref(false);
const catForm = reactive({ name: '', parent_id: null });

const form = reactive({
  name: '', 
  description: '', 
  price: 0, 
  image_url: '', 
  unit: '卷',
  category_id: null,
  variants: []
});

const fetchProducts = async () => {
  loading.value = true;
  try {
    const res = await axios.get('/products/?limit=500');
    products.value = res.data;
  } catch (e) { console.error(e); } finally { loading.value = false; }
};

// 获取分类树并扁平化
const fetchCategories = async () => {
  try {
    const res = await axios.get('/categories/?limit=100');
    rawCategories.value = res.data; 
  } catch (e) { console.error(e); }
};

// 递归扁平化分类树，用于 Select 显示和管理列表
const flatCategories = computed(() => {
  const buildTree = (items, parentId = null, level = 0) => {
    let result = [];
    items
      .filter(item => item.parent_id === parentId)
      .forEach(item => {
        result.push({ ...item, level });
        result = result.concat(buildTree(items, item.id, level + 1));
      });
    return result;
  };
  return buildTree(rawCategories.value);
});

const filteredProducts = computed(() => {
  if (!searchQuery.value) return products.value;
  const q = searchQuery.value.toLowerCase();
  return products.value.filter(p => p.name.toLowerCase().includes(q));
});

const getTotalStock = (p) => p.variants?.reduce((acc, v) => acc + (v.stock || 0), 0) || 0;
const getTotalIncoming = (p) => p.variants?.reduce((acc, v) => acc + (v.incoming_stock || 0), 0) || 0;

const openCreate = () => {
  currentId.value = null;
  resetForm();
  batchSpec.value = '2.5mm²'; 
  showModal.value = true;
};

const openEdit = (p) => {
  currentId.value = p.id;
  Object.assign(form, {
    name: p.name,
    description: p.description,
    price: p.price,
    image_url: p.image_url,
    unit: p.unit,
    category_id: p.category_id,
    variants: p.variants ? p.variants.map(v => ({
      ...v,
      incoming_stock: v.incoming_stock || 0,
      arrival_date: v.arrival_date || '',
      tier_min_qty: v.tier_min_qty || null,
      tier_discount: v.tier_discount || null
    })) : []
  });
  batchPrice.value = p.price;
  batchSpec.value = '';
  showModal.value = true;
};

const resetForm = () => {
  Object.assign(form, {
    name: '', description: '', price: 0, image_url: '', unit: '卷', category_id: null, variants: []
  });
};

const addVariant = () => {
  form.variants.push({
    spec: '', color: '', price: form.price, stock: 0, incoming_stock: 0, unit: form.unit
  });
};

const addStandardColors = () => {
  const colors = ['红', '兰', '黄', '绿', '双', '黑'];
  const specName = batchSpec.value || form.name || '标准规格';
  
  colors.forEach(color => {
    const exists = form.variants.some(v => v.spec === specName && v.color === color);
    if (!exists) {
      form.variants.push({
        spec: specName,
        color: color,
        price: batchPrice.value || form.price,
        stock: batchStock.value || 0,
        incoming_stock: 0,
        unit: form.unit
      });
    }
  });
  success(`已生成 ${specName} 的 6 种标准色`);
};

const removeVariant = (idx) => { form.variants.splice(idx, 1); };

// 打开新建分类弹窗
const openCategoryModal = () => {
  catForm.name = '';
  catForm.parent_id = null;
  showCategoryModal.value = true;
};

// 创建新分类
const createCategory = async () => {
  if (!catForm.name) return alert('请输入分类名称');
  try {
    const res = await axios.post('/categories/', catForm);
    success('分类创建成功');
    await fetchCategories(); // 刷新列表
    form.category_id = res.data.id; // 自动选中新分类
    // showCategoryModal.value = false; // 不关闭，方便连续添加
    catForm.name = ''; // 清空名称
  } catch (e) {
    showError('创建失败');
  }
};

// 删除分类
const deleteCategory = async (id) => {
  if (!confirm('确定要删除此分类吗？包含的子分类可能会受到影响。')) return;
  try {
    await axios.delete(`/categories/${id}`);
    success('分类已删除');
    await fetchCategories();
  } catch (e) {
    showError('删除失败: ' + (e.response?.data?.detail || e.message));
  }
};

const handleSave = async () => {
  if (!form.name) return alert("请输入商品名称");
  
  saving.value = true;
  try {
    const payload = {
      ...form,
      price: Number(form.price),
      variants: form.variants.map(v => ({
        ...v,
        price: Number(v.price),
        stock: Number(v.stock),
        incoming_stock: Number(v.incoming_stock || 0),
        tier_min_qty: v.tier_min_qty ? Number(v.tier_min_qty) : null,
        tier_discount: v.tier_discount ? Number(v.tier_discount) : null
      }))
    };
    
    if (currentId.value) {
      await axios.put(`/products/${currentId.value}`, payload);
      success("✅ 商品已更新");
    } else {
      await axios.post('/products/', payload);
      success("✅ 新商品创建成功");
    }
    
    showModal.value = false;
    await fetchProducts();
  } catch (e) {
    showError("保存失败: " + (e.response?.data?.detail || e.message));
  } finally {
    saving.value = false;
  }
};

const deleteProduct = async (id) => {
  if (!confirm("确定要删除这个商品吗？所有库存数据将丢失。")) return;
  try {
    await axios.delete(`/products/${id}`);
    success("已删除");
    fetchProducts();
  } catch(e) { showError("删除失败"); }
};

onMounted(() => {
  fetchProducts();
  fetchCategories();
});
</script>

<style scoped>
.lbl { @apply block text-xs font-bold text-gray-500 mb-1; }
.input-std { @apply w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none transition-all; }
.th-std { @apply px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider; }
.animate-fade-in-up { animation: fadeInUp 0.3s ease-out; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>