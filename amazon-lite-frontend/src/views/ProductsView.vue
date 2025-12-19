<template>
  <div class="bg-gray-50 min-h-screen pt-10 pb-12">
    <div class="max-w-[90rem] mx-auto px-4 sm:px-6 lg:px-8">
      
      <div class="mb-8 animate-fade-in-down">
        <h1 class="text-3xl font-bold text-gray-900">全线产品目录</h1>
        <p class="text-gray-500 mt-2">Amazon Cable 官方直营，原厂质保</p>
      </div>

      <div class="flex flex-col lg:flex-row gap-8">
        
        <aside class="hidden lg:block w-64 flex-shrink-0 animate-fade-in-left">
          <div class="sticky top-24 bg-white rounded-2xl shadow-sm border border-gray-100 p-4 overflow-hidden">
            <h3 class="font-bold text-gray-900 mb-4 px-2 text-lg">产品分类</h3>
            
            <nav class="space-y-1">
              <button 
                @click="selectCategory(null)"
                class="w-full group flex justify-between items-center px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 mb-2"
                :class="selectedCategoryId === null ? 'bg-orange-50 text-orange-600 shadow-sm' : 'text-gray-600 hover:bg-gray-50 hover:text-orange-600'"
              >
                <span class="group-hover:translate-x-1 transition-transform duration-200">全部产品</span>
                <span class="text-xs py-0.5 px-2 rounded-full transition-colors" 
                  :class="selectedCategoryId === null ? 'bg-orange-100 text-orange-600' : 'bg-gray-100 text-gray-400 group-hover:bg-orange-100 group-hover:text-orange-500'">
                  {{ allProducts.length }}
                </span>
              </button>

              <div v-for="parent in treeCategories" :key="parent.id" class="border-t border-gray-50 first:border-0">
                
                <button 
                  @click="toggleCategory(parent)"
                  class="w-full flex justify-between items-center px-3 py-3 text-sm font-bold text-gray-800 hover:text-orange-600 transition-colors"
                >
                  <span class="truncate">{{ parent.name }}</span>
                  
                  <svg v-if="parent.children && parent.children.length" 
                       class="w-4 h-4 text-gray-400 transition-transform duration-200" 
                       :class="{'rotate-180': parent.isOpen}"
                       fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                <div 
                  v-if="parent.children && parent.children.length" 
                  v-show="parent.isOpen" 
                  class="bg-gray-50 rounded-lg mb-2 overflow-hidden transition-all"
                >
                  <button 
                    v-for="child in parent.children" 
                    :key="child.id"
                    @click="selectCategory(child.id)"
                    class="w-full text-left pl-6 pr-3 py-2 text-xs font-medium text-gray-500 hover:text-orange-600 hover:bg-orange-50 transition-colors flex justify-between items-center"
                    :class="{'text-orange-600 bg-orange-50 font-bold': selectedCategoryId === child.id}"
                  >
                    <span class="truncate">{{ child.name }}</span>
                    <span class="text-[10px] bg-white px-1.5 py-0.5 rounded-full text-gray-400 border border-gray-100">
                      {{ getProductCount(child.id) }}
                    </span>
                  </button>
                </div>
              </div>
            </nav>
          </div>
        </aside>

        <main class="flex-1 space-y-12">
          
          <div v-if="loading" class="py-40 text-center">
            <div class="relative w-16 h-16 mx-auto">
               <div class="absolute inset-0 border-t-4 border-orange-500 border-solid rounded-full animate-spin"></div>
               <div class="absolute inset-2 border-b-4 border-gray-200 border-solid rounded-full animate-spin-reverse"></div>
            </div>
            <p class="mt-6 text-gray-500 font-medium animate-pulse">正在加载全量产品库...</p>
          </div>

          <div v-else class="space-y-16">
            <section 
              v-for="(cat, catIndex) in displayCategories" 
              :key="cat.id" 
              class="animate-fade-in-up"
              :style="{ animationDelay: `${catIndex * 50}ms` }"
            >
              <div class="flex items-center mb-8 border-b border-gray-200/60 pb-3">
                <div class="w-2 h-2 bg-orange-500 rounded-full mr-3 ring-4 ring-orange-100"></div>
                <h2 class="text-2xl font-bold text-gray-900">{{ cat.name }}</h2>
              </div>

              <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-5 gap-6">
                
                <div 
                  v-for="(product, prodIndex) in getProductsByCategory(cat.id)" 
                  :key="product.id"
                  class="product-card group bg-white rounded-2xl border border-gray-100 overflow-hidden hover:shadow-lg hover:border-orange-200 hover:-translate-y-1.5 transition-all duration-300 flex flex-col relative"
                  :style="{ animationDelay: `${ prodIndex * 30 }ms` }"
                >
                  <div class="aspect-[4/3] bg-gray-50 relative overflow-hidden cursor-pointer" @click="openVariantModal(product)">
                    <img :src="product.image_url" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 ease-in-out mix-blend-multiply">
                    <div v-if="isLoggedIn" class="absolute top-2 left-2 backdrop-blur-md bg-white/80 p-1 rounded-lg shadow-sm">
                       <span class="text-[10px] font-bold px-2 py-1 rounded-md bg-green-100 text-green-700">
                         现货充足
                       </span>
                    </div>
                  </div>
                  
                  <div class="p-5 flex flex-col flex-grow">
                    <h3 class="font-bold text-gray-900 mb-1.5 truncate transition-colors group-hover:text-orange-600 cursor-pointer" 
                        @click="openVariantModal(product)"
                        :title="product.name">
                        {{ product.name }}
                    </h3>
                    <p class="text-xs text-gray-500 line-clamp-2 mb-4 h-8 leading-relaxed">{{ product.description }}</p>
                    
                    <div class="mt-auto flex justify-between items-end pt-3 border-t border-dashed border-gray-100">
                      <div>
                        <p class="text-[10px] text-gray-400 mb-0.5">参考价</p>
                        <div class="text-orange-600 font-bold font-mono text-lg leading-none">
                          <span class="text-sm">¥</span>{{ getDisplayPrice(product) }}
                          <span class="text-xs text-gray-400 font-normal">
                            /{{ product.unit || product.variants?.[0]?.unit || '单位' }}
                          </span>
                        </div>
                      </div>
                      
                      <button 
                        @click.stop="openVariantModal(product)"
                        class="text-xs font-bold text-white bg-gray-900 px-3 py-2 rounded-lg hover:bg-orange-600 transition-all flex items-center shadow-md active:scale-95"
                      >
                        <svg class="w-3 h-3 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg>
                        选规格
                      </button>
                    </div>
                  </div>
                </div>

                <div v-if="getProductsByCategory(cat.id).length === 0" class="col-span-full py-12 text-center text-gray-400 text-sm bg-white rounded-2xl border-2 border-dashed border-gray-100">
                  该分类下暂无上架产品
                </div>
              </div>
            </section>
          </div>

        </main>
      </div>

      <ProductVariantModal 
        :is-open="isModalOpen" 
        :product="currentProduct"
        @close="isModalOpen = false"
        @add-to-cart="handleAddToCart"
      />
      <FloatingCart />

    </div>
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

const categories = ref([]); // 原始平铺分类
const treeCategories = ref([]); // 【新增】树形结构分类
const allProducts = ref([]);
const loading = ref(true);
const selectedCategoryId = ref(null);

// 弹窗状态
const isModalOpen = ref(false);
const currentProduct = ref({});

const fetchData = async () => {
  loading.value = true;
  try {
    // 获取分类和产品
    const [catRes, prodRes] = await Promise.all([
      api.get('/categories/?limit=100'), // 确保获取足够多的分类
      api.get('/products/?limit=500') 
    ]);
    
    // 1. 保存原始数据
    categories.value = catRes.data;
    allProducts.value = prodRes.data;

    // 2. 【核心逻辑】构建树形结构用于侧边栏
    // 假设后端返回的是平铺列表，我们手动组装 parent-child 关系
    const rawCats = catRes.data;
    const roots = rawCats.filter(c => !c.parent_id); // 找到顶级分类
    
    treeCategories.value = roots.map(root => ({
      ...root,
      isOpen: false, // 默认折叠
      children: rawCats.filter(c => c.parent_id === root.id) // 找到该父级下的子级
    }));

  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// 计算属性：决定右侧显示哪些分类的区块
const displayCategories = computed(() => {
  // 如果没选分类，显示所有的一级和二级分类（只要下面有产品）
  if (selectedCategoryId.value === null) {
    return categories.value;
  }
  
  // 如果选了某个分类
  const selectedId = selectedCategoryId.value;
  
  // 1. 找到这个分类本身
  const target = categories.value.find(c => c.id === selectedId);
  if (!target) return [];

  // 2. 如果它是父分类，显示它下面的子分类区块？或者只显示它自己？
  // 这里的逻辑：只显示选中的那个分类区块
  return [target];
});

// 点击左侧分类时的逻辑
const selectCategory = (id) => {
  selectedCategoryId.value = id;
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

// 展开/收起父分类
const toggleCategory = (parent) => {
  // 如果父分类没有子分类，直接当作点击筛选
  if (!parent.children || parent.children.length === 0) {
    selectCategory(parent.id);
  } else {
    // 否则切换折叠状态
    parent.isOpen = !parent.isOpen;
  }
};

const getProductsByCategory = (catId) => {
  // 简单的精确匹配：产品属于该 category_id
  return allProducts.value.filter(p => p.category_id === catId);
};

const getProductCount = (catId) => {
  return getProductsByCategory(catId).length;
};

// 辅助函数：显示价格区间
const getDisplayPrice = (product) => {
  if (product.variants && product.variants.length > 0) {
    const prices = product.variants.map(v => v.price);
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    if (min === max) return min;
    return `${min} - ${max}`;
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
/* 动画 Keyframes */
@keyframes fadeInUp { from { opacity: 0; transform: translate3d(0, 30px, 0) scale(0.98); } to { opacity: 1; transform: translate3d(0, 0, 0) scale(1); } }
@keyframes fadeInLeft { from { opacity: 0; transform: translate3d(-30px, 0, 0); } to { opacity: 1; transform: translate3d(0, 0, 0); } }
@keyframes fadeInDown { from { opacity: 0; transform: translate3d(0, -20px, 0); } to { opacity: 1; transform: translate3d(0, 0, 0); } }
@keyframes spin-reverse { to { transform: rotate(-360deg); } }

.animate-fade-in-up { animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; opacity: 0; }
.animate-fade-in-left { animation: fadeInLeft 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
.animate-fade-in-down { animation: fadeInDown 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
.animate-spin-reverse { animation: spin-reverse 1.5s linear infinite; }

.product-card { opacity: 0; animation: fadeInUp 0.7s cubic-bezier(0.25, 0.8, 0.25, 1) forwards; }
</style>