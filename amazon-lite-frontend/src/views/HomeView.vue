<template>
  <div class="bg-white">

    <section class="relative h-[90vh] bg-gray-900 text-white overflow-hidden">
      <div class="absolute inset-0 w-full h-full">
        <div v-for="(banner, index) in banners" :key="index"
          class="absolute inset-0 w-full h-full transition-opacity duration-1000 ease-in-out"
          :class="{ 'opacity-100 z-10': index === currentSlide, 'opacity-0 z-0': index !== currentSlide }">
          <img :src="banner.image" :alt="banner.title"
            class="w-full h-full object-cover opacity-60 transform scale-105 transition-transform duration-[10s]"
            :class="{ 'scale-110': index === currentSlide }">
          <div class="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/40 to-gray-900/30"></div>
        </div>
      </div>

      <div class="absolute inset-0 z-20 flex flex-col items-center justify-center text-center px-4 pt-10">
        <div v-if="banners[currentSlide]" :key="currentSlide" class="animate-fade-up">
          <span
            class="inline-block py-1 px-3 rounded-full bg-orange-500/20 border border-orange-500/50 text-orange-300 text-xs font-bold tracking-widest uppercase mb-6 backdrop-blur-md">
            {{ banners[currentSlide].tag }}
          </span>
          <h1
            class="text-4xl md:text-6xl lg:text-7xl font-extrabold tracking-tight mb-6 leading-tight max-w-5xl text-shadow-xl">
            <span v-html="banners[currentSlide].title"></span>
          </h1>
          <p class="text-lg md:text-xl font-light text-gray-200 mb-10 max-w-2xl mx-auto leading-relaxed">
            {{ banners[currentSlide].subtitle }}
          </p>
        </div>

        <div class="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-6 animate-fade-up animation-delay-200">
          <button @click="showSmartInquiry = true"
            class="bg-orange-600 text-white px-10 py-4 rounded-full font-bold text-lg hover:bg-orange-500 transition-all hover:scale-105 shadow-[0_0_20px_rgba(234,88,12,0.5)] flex items-center justify-center group">
            <svg class="w-6 h-6 mr-2 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
            立即询价
            <span class="ml-2 text-xs bg-white/20 px-2 py-0.5 rounded text-white font-normal group-hover:bg-white/30">上传图纸/清单</span>
          </button>
          
          <button @click="scrollToProducts"
            class="px-8 py-4 rounded-full font-bold text-lg text-white border-2 border-white/30 hover:bg-white/10 hover:border-white transition-all flex items-center justify-center backdrop-blur-sm cursor-pointer">
            现货产品
          </button>
        </div>
      </div>

      <div class="absolute bottom-8 left-0 right-0 z-30 flex justify-center space-x-3">
        <button v-for="(_, index) in banners" :key="index" @click="switchSlide(index)"
          class="w-3 h-3 rounded-full transition-all duration-300"
          :class="index === currentSlide ? 'bg-orange-500 w-8' : 'bg-white/50 hover:bg-white'"></button>
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

    <section class="bg-white border-t border-gray-100 py-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-row justify-between items-end mb-10">
          <div>
            <h2 class="text-3xl font-bold text-gray-900 mb-2">行业资讯 & 动态</h2>
            <p class="text-gray-500">聚焦电力传输前沿技术，分享企业最新里程碑</p>
          </div>
          <button @click="$router.push('/news')" class="group flex items-center text-sm font-bold text-orange-600 hover:text-orange-700 transition-colors">
            查看全部新闻
            <div class="ml-2 w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center group-hover:bg-orange-200 transition-colors">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
            </div>
          </button>
        </div>

        <div v-if="newsLoading" class="text-center py-10 text-gray-400">加载资讯中...</div>
        <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div v-for="news in newsList.slice(0, 3)" :key="news.id" @click="$router.push(`/news/${news.id}`)" class="group cursor-pointer flex flex-col hover:-translate-y-1 transition-transform duration-300">
            <div class="aspect-video bg-gray-100 rounded-xl overflow-hidden mb-4 relative">
              <img :src="news.image_url" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
              <div class="absolute bottom-0 left-0 bg-orange-600 text-white text-xs font-bold px-3 py-1 rounded-tr-lg">{{ new Date(news.created_at).toLocaleDateString() }}</div>
            </div>
            <h3 class="text-lg font-bold text-gray-900 mb-2 group-hover:text-orange-600 transition-colors line-clamp-2">{{ news.title }}</h3>
            <p class="text-sm text-gray-500 line-clamp-3 mb-4 flex-grow">{{ news.summary }}</p>
            <div class="text-sm font-bold text-orange-600 group-hover:translate-x-1 transition-transform flex items-center mt-auto">阅读全文 &rarr;</div>
          </div>
        </div>
      </div>
    </section>

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
const { products, loading, fetchProducts } = useProducts();
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

let slideInterval;
const nextSlide = () => { currentSlide.value = (currentSlide.value + 1) % banners.value.length; };
const switchSlide = (index) => { currentSlide.value = index; resetSlideTimer(); };
const resetSlideTimer = () => { clearInterval(slideInterval); slideInterval = setInterval(nextSlide, 6000); };

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

// 新闻
const newsList = ref([]);
const newsLoading = ref(false);
const fetchNews = async () => {
  newsLoading.value = true;
  try {
    const res = await api.get('/news/', { params: { limit: 3 } });
    newsList.value = res.data;
  } catch (error) { console.error("Fetch news failed", error); } finally { newsLoading.value = false; }
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
  fetchProducts();
  resetSlideTimer();
  fetchMetalPrices();
  priceInterval = setInterval(fetchMetalPrices, 60000);
  fetchNews();
});

onUnmounted(() => {
  clearInterval(slideInterval);
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