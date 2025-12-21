<template>
  <div class="bg-gray-50 min-h-screen pt-24 pb-12">
    <div class="max-w-[90rem] mx-auto px-4 sm:px-6 lg:px-8">
      
      <div class="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 flex items-center">
            <svg class="w-6 h-6 mr-2 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
            产品选型目录
          </h1>
          <p class="text-xs text-gray-500 mt-1">实时库存数据 | 每日 09:00 更新价格</p>
        </div>
        
        <div class="flex gap-2">
           <button class="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium hover:border-orange-500 hover:text-orange-600 transition-colors">
             只看现货
           </button>
           <button class="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors flex items-center">
             <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
             下载报价单 PDF
           </button>
        </div>
      </div>

      <div class="flex flex-col lg:flex-row gap-6">
        
        <aside class="w-full lg:w-64 flex-shrink-0">
          <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden sticky top-24">
            <div class="p-4 bg-gray-50 border-b border-gray-200 font-bold text-gray-800 text-sm">分类导航</div>
            <nav class="p-2 space-y-1 max-h-[70vh] overflow-y-auto custom-scrollbar">
              <button @click="selectCategory(null)" class="w-full text-left px-3 py-2 text-sm rounded-lg hover:bg-gray-100 transition-colors" :class="selectedCategoryId === null ? 'font-bold text-orange-600 bg-orange-50' : 'text-gray-600'">
                全部系列
              </button>
              
              <div v-for="parent in treeCategories" :key="parent.id" class="mt-2">
                <div @click="toggleCategory(parent)" class="flex items-center justify-between px-3 py-2 text-sm font-bold text-gray-900 cursor-pointer hover:text-orange-600">
                  {{ parent.name }}
                  <span class="text-xs text-gray-400 transform transition-transform" :class="parent.isOpen ? 'rotate-180' : ''">▼</span>
                </div>
                <div v-show="parent.isOpen" class="pl-2 space-y-0.5">
                  <button v-for="child in parent.children" :key="child.id" @click="selectCategory(child.id)"
                    class="w-full text-left px-3 py-1.5 text-xs rounded-md transition-colors flex justify-between group"
                    :class="selectedCategoryId === child.id ? 'text-orange-600 bg-orange-50 font-bold' : 'text-gray-500 hover:bg-gray-50'">
                    <span>{{ child.name }}</span>
                    <span class="text-[10px] text-gray-300 group-hover:text-gray-400">{{ getProductCount(child.id) }}</span>
                  </button>
                </div>
              </div>
            </nav>
          </div>
        </aside>

        <main class="flex-1">
          <div v-if="loading" class="py-20 text-center text-gray-400">数据加载中...</div>
          
          <div v-else class="space-y-8">
            <section v-for="cat in displayCategories" :key="cat.id" class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              
              <div class="bg-gray-50/50 px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                <h2 class="text-lg font-bold text-gray-900 flex items-center">
                  <span class="w-1.5 h-4 bg-orange-500 rounded mr-2"></span>
                  {{ cat.name }}
                </h2>
                <span class="text-xs text-gray-400">共 {{ getProductsByCategory(cat.id).length }} 款型号</span>
              </div>

              <div class="hidden md:block">
                <table class="w-full text-left border-collapse">
                  <thead class="bg-gray-50 text-xs uppercase text-gray-500 font-medium">
                    <tr>
                      <th class="px-6 py-3 w-20">图片</th>
                      <th class="px-6 py-3">产品型号/名称</th>
                      <th class="px-6 py-3">核心参数</th>
                      <th class="px-6 py-3">库存状态</th>
                      <th class="px-6 py-3 text-right">参考单价</th>
                      <th class="px-6 py-3 text-right">操作</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-100">
                    <tr v-for="product in getProductsByCategory(cat.id)" :key="product.id" class="hover:bg-orange-50/30 transition-colors group cursor-pointer" @click="openVariantModal(product)">
                      <td class="px-6 py-3">
                        <div class="w-12 h-12 bg-gray-100 rounded border border-gray-200 overflow-hidden">
                          <img :src="product.image_url" class="w-full h-full object-cover mix-blend-multiply">
                        </div>
                      </td>
                      <td class="px-6 py-3">
                        <div class="font-bold text-gray-900 group-hover:text-orange-600">{{ product.name }}</div>
                        <div class="text-xs text-gray-400">{{ product.category_detail?.name }}</div>
                      </td>
                      <td class="px-6 py-3">
                        <div class="flex gap-2">
                          <span class="px-2 py-0.5 rounded text-[10px] bg-gray-100 text-gray-600 border border-gray-200">国标纯铜</span>
                          <span class="px-2 py-0.5 rounded text-[10px] bg-gray-100 text-gray-600 border border-gray-200">XLPE</span>
                        </div>
                      </td>
                      <td class="px-6 py-3">
                         <div class="flex items-center text-xs font-medium text-green-600">
                           <span class="w-2 h-2 bg-green-500 rounded-full mr-1.5 animate-pulse"></span>
                           现货足
                         </div>
                      </td>
                      <td class="px-6 py-3 text-right">
                        <div class="font-mono font-bold text-orange-600">
                          <span class="text-xs">¥</span>{{ getDisplayPrice(product) }}
                        </div>
                        <div class="text-[10px] text-gray-400">/ {{ product.unit || '米' }}</div>
                      </td>
                      <td class="px-6 py-3 text-right">
                        <button class="text-xs bg-gray-900 hover:bg-orange-600 text-white px-3 py-1.5 rounded transition-colors shadow-sm">
                          选规格
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div class="md:hidden divide-y divide-gray-100">
                <div v-for="product in getProductsByCategory(cat.id)" :key="product.id" @click="openVariantModal(product)" class="p-4 flex gap-4 active:bg-gray-50">
                   <div class="w-20 h-20 bg-gray-100 rounded border border-gray-200 flex-shrink-0">
                     <img :src="product.image_url" class="w-full h-full object-cover">
                   </div>
                   <div class="flex-1 flex flex-col justify-between">
                     <div>
                       <h3 class="font-bold text-gray-900 line-clamp-1">{{ product.name }}</h3>
                       <div class="flex gap-1 mt-1">
                         <span class="text-[10px] bg-gray-100 px-1.5 rounded text-gray-500">国标</span>
                       </div>
                     </div>
                     <div class="flex justify-between items-end">
                       <span class="font-mono font-bold text-orange-600">¥{{ getDisplayPrice(product) }}</span>
                       <button class="text-xs bg-gray-900 text-white px-3 py-1.5 rounded">选规格</button>
                     </div>
                   </div>
                </div>
              </div>

              <div v-if="getProductsByCategory(cat.id).length === 0" class="p-8 text-center text-gray-400 text-sm">
                暂无产品
              </div>
            </section>
          </div>
        </main>

      </div>
    </div>

    <ProductVariantModal :is-open="isModalOpen" :product="currentProduct" @close="isModalOpen = false" @add-to-cart="handleAddToCart" />
    <FloatingCart />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '../api/axios';
import { useAuth } from '../composables/useAuth';
import { useCart } from '../composables/useCart';
import ProductVariantModal from '../components/ProductVariantModal.vue';
import FloatingCart from '../components/FloatingCart.vue';

const { isLoggedIn } = useAuth();
const { addToCart } = useCart();

const categories = ref([]);
const treeCategories = ref([]);
const allProducts = ref([]);
const loading = ref(true);
const selectedCategoryId = ref(null);

const isModalOpen = ref(false);
const currentProduct = ref({});

const fetchData = async () => {
  loading.value = true;
  try {
    const [catRes, prodRes] = await Promise.all([
      api.get('/categories/?limit=100'),
      api.get('/products/?limit=500') 
    ]);
    categories.value = catRes.data;
    allProducts.value = prodRes.data;

    // 构建分类树
    const rawCats = catRes.data;
    const roots = rawCats.filter(c => !c.parent_id);
    treeCategories.value = roots.map(root => ({
      ...root,
      isOpen: true, // 默认展开，方便查看
      children: rawCats.filter(c => c.parent_id === root.id)
    }));

  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const displayCategories = computed(() => {
  if (selectedCategoryId.value === null) return categories.value.filter(c => !c.parent_id); // 默认只显示一级分类块
  const target = categories.value.find(c => c.id === selectedCategoryId.value);
  return target ? [target] : [];
});

const selectCategory = (id) => {
  selectedCategoryId.value = id;
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const toggleCategory = (parent) => {
  parent.isOpen = !parent.isOpen;
};

const getProductsByCategory = (catId) => {
  // 查找该分类下的产品，如果是父分类，应该包含子分类产品(这里简化处理，只匹配当前id)
  // 实际业务中可能需要递归查找所有子分类ID
  return allProducts.value.filter(p => p.category_id === catId);
};

const getProductCount = (catId) => {
  return allProducts.value.filter(p => p.category_id === catId).length;
};

const getDisplayPrice = (product) => {
  if (product.variants && product.variants.length > 0) {
    const prices = product.variants.map(v => v.price);
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    if (min === max) return min;
    return `${min}-${max}`;
  }
  return product.price || '询价';
};

const openVariantModal = (product) => {
  currentProduct.value = product;
  isModalOpen.value = true;
};

const handleAddToCart = async (items) => {
  for (const item of items) {
    await addToCart(item.variantId, item.quantity);
  }
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
/* 自定义滚动条 */
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: #f1f1f1; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #9ca3af; }
</style>