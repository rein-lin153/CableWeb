<template>
  <div class="bg-white">

    <section class="bg-[#0f172a] text-white pt-24 pb-12 min-h-[600px] flex items-center relative overflow-hidden">
  <div class="absolute inset-0 z-0 opacity-20 bg-[url('/bz1.jpg')] bg-cover bg-center mix-blend-overlay"></div>
  <div class="absolute inset-0 bg-gradient-to-r from-[#0f172a] via-[#0f172a]/90 to-transparent z-0"></div>

  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
    
    <div class="space-y-8 animate-fade-in-up">
      <div>
        <span class="text-orange-500 font-bold tracking-widest uppercase text-sm mb-2 block">Factory Direct Supply</span>
        <h1 class="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight leading-tight">
          源头工厂直销<br>
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-red-500">今日下单，次日送达</span>
        </h1>
      </div>
      
      <p class="text-gray-400 text-lg max-w-xl leading-relaxed">
        Amazon Cable 专注工业电缆制造 20 年。自有车队覆盖全境，为您节省 30% 中间商差价。支持工地现场验收，货到付款。
      </p>

      <div class="flex flex-col sm:flex-row gap-4">
        <button @click="$router.push('/products')" class="px-8 py-4 bg-orange-600 hover:bg-orange-500 text-white rounded-lg font-bold text-lg transition-all shadow-lg shadow-orange-600/30 flex items-center justify-center">
          查看现货库存
          <svg class="w-5 h-5 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" /></svg>
        </button>
        <button @click="showSmartInquiry = true" class="px-8 py-4 bg-white/10 hover:bg-white/20 border border-white/30 backdrop-blur-sm text-white rounded-lg font-bold text-lg transition-all flex items-center justify-center">
          上传清单 (BOM) 报价
        </button>
      </div>

      <div class="pt-8 border-t border-gray-800 grid grid-cols-3 gap-6 text-center">
        <div>
          <div class="text-2xl font-bold text-white">GB/T</div>
          <div class="text-xs text-gray-500 mt-1">严格执行国标</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-white">24h</div>
          <div class="text-xs text-gray-500 mt-1">现货闪电发货</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-white">100%</div>
          <div class="text-xs text-gray-500 mt-1">纯铜保检测</div>
        </div>
      </div>
    </div>

    <div class="bg-white/5 border border-white/10 rounded-2xl p-6 lg:p-8 backdrop-blur-md shadow-2xl">
      <div class="flex justify-between items-center mb-6">
        <h3 class="text-xl font-bold text-white flex items-center">
          <span class="w-2 h-6 bg-orange-500 rounded-sm mr-3"></span>
          今日铜价指数
        </h3>
        <span class="text-xs text-gray-400">更新于: {{ new Date().toLocaleDateString() }}</span>
      </div>

      <div class="grid grid-cols-2 gap-4 mb-8">
        <div class="bg-white/5 p-4 rounded-xl border border-white/5">
          <div class="text-gray-400 text-xs mb-1">LME 伦敦铜 ($)</div>
          <div class="text-2xl font-mono font-bold text-green-400">$9,120</div>
          <div class="text-xs text-green-500 mt-1 flex items-center">▲ 1.2% <span class="text-gray-500 ml-1">昨日</span></div>
        </div>
        <div class="bg-white/5 p-4 rounded-xl border border-white/5">
          <div class="text-gray-400 text-xs mb-1">SMM 长江现货 (¥)</div>
          <div class="text-2xl font-mono font-bold text-orange-400">¥72,300</div>
          <div class="text-xs text-orange-500 mt-1 flex items-center">▲ 0.5% <span class="text-gray-500 ml-1">昨日</span></div>
        </div>
      </div>

      <div class="space-y-4">
        <h4 class="text-sm font-bold text-gray-300 uppercase tracking-wider">快速通道</h4>
        <button @click="$router.push('/products?category=yjv')" class="w-full text-left px-4 py-3 bg-white/5 hover:bg-orange-600 hover:text-white border border-white/10 rounded-lg transition-colors flex justify-between items-center group">
          <span class="font-medium text-gray-300 group-hover:text-white">YJV 电力电缆 (现货)</span>
          <span class="text-gray-500 group-hover:text-white">→</span>
        </button>
        <button @click="$router.push('/products?category=bv')" class="w-full text-left px-4 py-3 bg-white/5 hover:bg-orange-600 hover:text-white border border-white/10 rounded-lg transition-colors flex justify-between items-center group">
          <span class="font-medium text-gray-300 group-hover:text-white">BV 家装电线</span>
          <span class="text-gray-500 group-hover:text-white">→</span>
        </button>
        <div class="text-center pt-2">
           <a href="#" class="text-sm text-gray-500 hover:text-orange-400 underline decoration-dashed">下载 2025 最新产品选型手册 PDF</a>
        </div>
      </div>
    </div>
  </div>
</section>

    <div class="bg-gray-50 border-y border-gray-200 transition-colors duration-300"
      :class="currency === 'CNY' ? 'bg-red-50/30' : 'bg-blue-50/30'">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-col sm:flex-row justify-between items-center text-sm text-gray-600">
        <div class="flex items-center space-x-4 mb-2 sm:mb-0">
          <div class="flex items-center">
            <span class="w-2.5 h-2.5 rounded-full mr-2 animate-pulse" :class="currency === 'CNY' ? 'bg-red-600' : 'bg-blue-600'"></span>
            <span class="font-bold text-gray-900 mr-2">{{ currentPriceData.source }}:</span>
          </div>
          <div class="flex items-baseline space-x-2">
            <span class="font-mono text-xl font-extrabold tracking-tight" :class="currency === 'CNY' ? 'text-red-700' : 'text-blue-700'">
              {{ currentPriceData.symbol }}{{ currentPriceData.price ? currentPriceData.price.toLocaleString() : '0' }}
            </span>
            <span class="text-xs text-gray-500 font-medium">/ 吨</span>
          </div>
          <span class="text-xs px-2 py-0.5 rounded font-medium flex items-center" :class="currentPriceData.change > 0 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'">
            <span v-if="currentPriceData.change > 0">▲</span><span v-else>▼</span>{{ Math.abs(currentPriceData.change) }}%
          </span>
        </div>
        <div class="flex items-center space-x-6">
          <div class="flex bg-gray-200 rounded-lg p-1">
            <button @click="currency = 'CNY'" class="px-3 py-1 rounded-md text-xs font-bold transition-all duration-200" :class="currency === 'CNY' ? 'bg-white text-red-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'">RMB ¥</button>
            <button @click="currency = 'USD'" class="px-3 py-1 rounded-md text-xs font-bold transition-all duration-200" :class="currency === 'USD' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'">USD $</button>
          </div>
          <div class="hidden md:flex flex-col items-end text-[10px] leading-tight text-gray-400">
            <div>更新于: {{ priceDatabase.updated || '获取中...' }}</div>
            <div v-if="priceDatabase.exchange_rate" class="text-gray-500 font-mono mt-0.5">参考汇率: 1 USD ≈ {{ priceDatabase.exchange_rate }} CNY</div>
          </div>
        </div>
      </div>
    </div>

    <main id="product-section" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
      <div class="flex flex-row justify-between items-end mb-8">
        <div>
          <h2 class="text-3xl font-bold text-gray-900 mb-2">热门规格现货</h2>
          <p class="text-gray-500">严格执行 GB/T 标准，精选热销型号</p>
        </div>
        <button @click="$router.push('/products')" class="group flex items-center text-sm font-bold text-orange-600 hover:text-orange-700 transition-colors">
          查看全部产品
          <div class="ml-2 w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center group-hover:bg-orange-200 transition-colors">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
          </div>
        </button>
      </div>

      <div v-if="loading" class="py-20 flex flex-col items-center justify-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mb-4"></div>
        <span class="text-gray-400 text-sm">正在同步仓储数据...</span>
      </div>

      <div v-else>
        <swiper :slides-per-view="1" :space-between="24" :loop="products.length > 4"
          :autoplay="{ delay: 3000, disableOnInteraction: false }"
          :breakpoints="{ 640: { slidesPerView: 2 }, 1024: { slidesPerView: 4 } }" :modules="[Autoplay]"
          class="product-swiper py-4 px-1">
          <swiper-slide v-for="product in products.slice(0, 10)" :key="product.id" class="h-auto">

            <div class="group h-full bg-white rounded-xl border border-gray-100 hover:border-orange-300 hover:shadow-xl transition-all duration-300 flex flex-col overflow-hidden relative">
              <div class="aspect-square bg-gray-100 relative overflow-hidden cursor-pointer" @click="openVariantModal(product)">
                <div v-if="isLoggedIn" class="absolute top-3 left-3 z-10">
                  <span class="bg-green-600 text-white text-[10px] px-2 py-1 rounded-sm uppercase tracking-wider font-bold shadow-sm">现货</span>
                </div>
                <img :src="product.image_url" :alt="product.name" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 mix-blend-multiply">
              </div>

              <div class="p-4 flex flex-col flex-grow">
                <div class="mb-1"><span class="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500">{{ product.category_detail?.name || '工业线缆' }}</span></div>
                <h3 class="text-base font-bold text-gray-900 group-hover:text-orange-600 transition-colors line-clamp-1 mb-1 cursor-pointer" @click="openVariantModal(product)">{{ product.name }}</h3>

                <div class="mt-auto pt-3 border-t border-gray-50 flex justify-between items-end">
                  <div class="text-orange-600 font-bold font-mono">
                    <span class="text-xs">¥</span>{{ getDisplayPrice(product) }}
                    <span class="text-xs text-gray-400 font-normal">/{{ product.unit || product.variants?.[0]?.unit || '单位' }}</span>
                  </div>

                  <button @click.stop="openVariantModal(product)" class="text-xs bg-gray-900 text-white px-3 py-1.5 rounded hover:bg-orange-600 transition-all shadow-md flex items-center">
                    选规格
                  </button>
                </div>
              </div>
            </div>

          </swiper-slide>
        </swiper>
      </div>
    </main>

    

    <footer class="bg-gray-950 py-20 text-gray-400 text-sm mt-0 border-t border-gray-900">
      <div class="max-w-7xl mx-auto px-4 grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
        <div class="col-span-1 md:col-span-2">
          <div class="flex items-center mb-6">
            <div class="w-8 h-8 rounded-full bg-orange-500 flex items-center justify-center mr-3 shadow-lg shadow-orange-500/20">
              <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
            </div>
            <h3 class="text-white text-2xl font-bold tracking-tight">Amazon <span class="text-orange-500">Cable</span></h3>
          </div>
          <p class="mb-6 max-w-md text-gray-500 leading-relaxed">作为全球基础设施建设的可靠合作伙伴，我们要致力于提供最优质的电力传输与信号控制解决方案。</p>
        </div>
        <div>
          <h4 class="text-white font-bold mb-6 uppercase tracking-wider">快速链接</h4>
          <ul class="space-y-4">
            <li><a href="#" class="hover:text-orange-500 transition-colors">下载选型手册</a></li>
            <li><a href="#" class="hover:text-orange-500 transition-colors">今日铜价</a></li>
          </ul>
        </div>
        <div>
          <h4 class="text-white font-bold mb-6 uppercase tracking-wider">联系我们</h4>
          <ul class="space-y-4">
            <li>400-888-8888</li>
            <li>sales@amazoncable.com</li>
            <li>江苏省无锡市官林工业园 88 号</li>
          </ul>
        </div>
      </div>
      <div class="max-w-7xl mx-auto px-4 pt-8 border-t border-gray-900 text-center">
        <p>&copy; 2025 Amazon Cable Co., Ltd. All rights reserved.</p>
      </div>
    </footer>

    <SmartInquiryModal :is-open="showSmartInquiry" @close="showSmartInquiry = false" />

    <ProductVariantModal :is-open="isModalOpen" :product="currentProduct" @close="isModalOpen = false" @add-to-cart="handleAddToCart" />
    <FloatingCart />

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import api from '../api/axios';
import { useAuth } from '../composables/useAuth';
import { useRouter } from 'vue-router';
import { useProducts } from '../composables/useProducts';
import SmartInquiryModal from '../components/SmartInquiryModal.vue'; // 【新增】引入新组件

import ProductVariantModal from '../components/ProductVariantModal.vue';
import FloatingCart from '../components/FloatingCart.vue';
import { useCart } from '../composables/useCart';

import { Swiper, SwiperSlide } from 'swiper/vue';
import { Autoplay } from 'swiper/modules';
import 'swiper/css';
import { useI18n } from 'vue-i18n';

const { isLoggedIn } = useAuth();
const router = useRouter();
const { products, loading, fetchAllData } = useProducts();
const { t } = useI18n();
const { addToCart } = useCart();

// 【新增】智能询价弹窗状态
const showSmartInquiry = ref(false);

const isModalOpen = ref(false);
const currentProduct = ref({});

const scrollToProducts = () => {
  // ✅ 新代码：直接跳转到产品列表页
  router.push('/products');
};

// 轮播图数据
const currentSlide = ref(0);
const banners = computed(() => [
  {
    image: '/bz1.jpg',
    tag: t('hero.slides[0].tag'),
    title: t('hero.slides[0].title'),
    subtitle: t('hero.slides[0].subtitle')
  },
  {
    image: '/bz2.jpg',
    tag: t('hero.slides[1].tag'),
    title: t('hero.slides[1].title'),
    subtitle: t('hero.slides[1].subtitle')
  },
  {
    image: '/bz3.jpg',
    tag: t('hero.slides[2].tag'),
    title: t('hero.slides[2].title'),
    subtitle: t('hero.slides[2].subtitle')
  }
]);


// 铜价
const currency = ref('CNY');
const priceDatabase = ref({ CNY: { source: '沪铜主连', symbol: '¥', price: 0, change: 0 }, USD: { source: 'LME 伦敦铜', symbol: '$', price: 0, change: 0 }, exchange_rate: 0, updated: '' });
const currentPriceData = computed(() => priceDatabase.value[currency.value] || { source: 'Loading...', symbol: '', price: 0, change: 0 });
const fetchMetalPrices = async () => {
  try {
    const response = await api.get('/meta/prices');
    if (response.data) priceDatabase.value = response.data;
  } catch (error) { console.error("无法获取实时铜价:", error); }
};


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

let priceInterval = null;

onMounted(() => {
  fetchAllData(); // 调用新方法
  fetchMetalPrices();
  priceInterval = setInterval(fetchMetalPrices, 60000);
});

onUnmounted(() => {
  if (priceInterval) clearInterval(priceInterval);
});
</script>

<style scoped>
.text-shadow-xl {
  text-shadow: 0 4px 10px rgba(0, 0, 0, 0.7);
}

@keyframes fade-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-up {
  animation: fade-up 0.8s ease-out forwards;
}

.animation-delay-200 {
  animation-delay: 0.2s;
  opacity: 0;
}
</style>