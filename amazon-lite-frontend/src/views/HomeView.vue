<template>
  <div class="bg-slate-50 min-h-screen font-sans text-slate-800">
    
    <section class="relative pt-24 pb-24 px-4 sm:px-6 lg:px-8 overflow-hidden bg-[#0F172A]">
      <div class="absolute inset-0 bg-slate-900"></div>
      <div class="absolute inset-0" 
           style="background-image: linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), 
           linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px); 
           background-size: 40px 40px;">
      </div>
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-3xl h-64 bg-blue-500/10 blur-[100px] rounded-full pointer-events-none"></div>

      <div class="relative z-20 max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
        
        <div class="lg:col-span-7 space-y-8 pt-6">
          <div class="inline-flex items-center space-x-2">
            <span class="px-3 py-1 rounded bg-blue-900/40 border border-blue-700/50 text-blue-300 text-xs font-bold tracking-wider uppercase">
              ISO 9001 认证工厂
            </span>
            <span class="px-3 py-1 rounded bg-orange-900/30 border border-orange-700/50 text-orange-300 text-xs font-bold tracking-wider uppercase flex items-center">
              <span class="w-1.5 h-1.5 rounded-full bg-orange-500 mr-2 animate-pulse"></span>
              库存实时同步
            </span>
          </div>

          <h1 class="text-4xl md:text-6xl font-extrabold tracking-tight text-white leading-tight">
            工程电缆<span class="text-blue-400">数字云仓</span> <br>
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-amber-300">
              源头直发 · 降本增效
            </span>
          </h1>

          <p class="text-base md:text-lg text-slate-400 max-w-xl leading-relaxed border-l-2 border-slate-700 pl-4">
            专注服务建筑承包商与批发商。
            <br>
            告别层层加价，我们提供<span class="text-slate-200 font-bold">透明的出厂价格</span>与<span class="text-slate-200 font-bold">工业级物流配送</span>体系。每一米电缆均符合国标 (GB/T) 严苛检测。
          </p>

          <div class="flex flex-wrap gap-4 pt-4">
            <button @click="$router.push('/products')" class="px-6 py-3.5 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white rounded-lg font-bold text-lg shadow-lg shadow-blue-900/30 transition-all flex items-center group border border-blue-500/30">
              选型目录
              <svg class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
            </button>
            
            <button @click="$router.push('/quick-order')" class="px-6 py-3.5 bg-orange-600 hover:bg-orange-500 text-white border border-orange-500 rounded-lg font-bold text-lg transition-all shadow-lg shadow-orange-900/20 flex items-center">
              <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
              文本下单
            </button>

            <button @click="showSmartInquiry = true" class="px-6 py-3.5 bg-slate-800/80 hover:bg-slate-700 text-slate-200 border border-slate-600 rounded-lg font-bold text-lg transition-all backdrop-blur-sm flex items-center">
              <svg class="w-5 h-5 mr-2 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
              BOM 报价
            </button>
          </div>
          
          <div class="pt-8 border-t border-slate-800/50 mt-8">
            <p class="text-xs font-bold text-slate-500 uppercase mb-4 tracking-wider flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              ENGINEERING TOOLKIT · 工程师工具箱
            </p>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
               <button @click="$router.push('/tools/voltage-drop')" class="flex items-center gap-3 p-3 rounded-lg bg-slate-800/60 hover:bg-slate-700/80 border border-slate-700 hover:border-yellow-500/50 transition-all group text-left">
                  <div class="w-8 h-8 rounded bg-yellow-500/10 flex items-center justify-center text-yellow-400 group-hover:bg-yellow-500 group-hover:text-white transition-colors">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                  </div>
                  <div>
                    <div class="text-xs font-bold text-slate-300 group-hover:text-white">电压降计算</div>
                    <div class="text-[10px] text-slate-500">线缆截面校验</div>
                  </div>
               </button>
               </div>
          </div>
        </div>

        <div class="lg:col-span-5 space-y-6 pt-6">
          
          <div class="bg-white rounded-lg shadow-2xl border-t-4 border-orange-500 p-6 relative overflow-hidden group">
             <div class="absolute -right-4 -top-4 w-24 h-24 bg-orange-500/5 rounded-full blur-2xl group-hover:bg-orange-500/10 transition-colors"></div>

             <div class="flex justify-between items-start mb-6 relative">
                <div>
                  <h3 class="font-bold text-slate-900 text-lg flex items-center">
                    <svg class="w-5 h-5 mr-2 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
                    SMM 长江现货铜价
                  </h3>
                  <p class="text-xs text-slate-400 mt-1 font-mono">CODE: CU-ETP-999</p>
                </div>
                <div class="text-right">
                  <span class="block text-3xl font-black text-slate-900 font-mono tracking-tighter">
                    {{ copperPrice.symbol }}{{ copperPrice.price ? copperPrice.price.toLocaleString() : '---' }}
                  </span>
                  <span class="inline-flex items-center text-xs font-bold text-slate-500 bg-slate-50 px-2 py-1 rounded mt-1 border border-slate-100">
                    更新于: {{ copperPrice.updated ? copperPrice.updated.split(' ')[1] : '--:--' }}
                  </span>
                </div>
             </div>
             
             <div class="bg-slate-50 rounded border-l-2 border-slate-800 p-3 flex items-start">
                <svg class="w-5 h-5 text-slate-800 mr-2 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                <div class="text-xs text-slate-600 leading-relaxed">
                   <span class="font-bold text-slate-800 block mb-1">系统提示：</span>
                   每日 09:30 同步最新盘价。当前价格仅供参考，下单时请以实时结算价为准。
                </div>
             </div>
          </div>

          <div class="bg-slate-800/80 backdrop-blur-md rounded-lg shadow-lg border border-slate-700 p-6">
              <div class="flex items-center justify-between mb-4">
                <label class="text-sm font-bold text-white flex items-center">
                  <svg class="w-4 h-4 mr-2 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0121 18.382V7.618a1 1 0 01-.806-.984l-4.647-2.324A1 1 0 0115 5.236V16.764c0 .445.232.855.618 1.09L9 20z" /></svg>
                  物流追踪 / Track Order
                </label>
              </div>
              <div class="relative flex">
                <input 
                  v-model="trackQuery" 
                  @keyup.enter="quickTrack" 
                  type="text" 
                  placeholder="请输入订单号 (如: 10023)..." 
                  class="flex-1 bg-slate-900/50 border border-slate-600 text-white rounded-l px-4 py-3 text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500 outline-none placeholder-slate-500"
                >
                <button 
                  @click="quickTrack" 
                  class="bg-blue-600 hover:bg-blue-500 text-white px-5 rounded-r text-sm font-bold transition-colors"
                  :disabled="tracking"
                >
                  {{ tracking ? '...' : '查询' }}
                </button>
              </div>
              <div v-if="trackResult" class="mt-3 p-3 bg-slate-700/50 border border-slate-600 text-blue-300 text-xs rounded animate-fade-in-up whitespace-pre-line">
                 {{ trackResult }}
              </div>
          </div>

        </div>
      </div>
    </section>

    <section class="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-end mb-8">
        <div>
          <h2 class="text-2xl font-bold text-slate-900">工程常用现货</h2>
          <p class="text-sm text-slate-500 mt-1">当日下单，当日发车</p>
        </div>
        <button @click="$router.push('/products')" class="text-sm font-bold text-blue-600 hover:text-blue-700 flex items-center">
          全部产品 <span class="ml-1">→</span>
        </button>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
         <div v-for="cat in categories.slice(0, 4)" :key="cat.id" 
              @click="$router.push({ path: '/products', query: { cat: cat.id } })"
              class="group bg-white rounded-xl p-5 border border-gray-100 shadow-sm hover:shadow-md hover:border-blue-200 transition-all cursor-pointer">
           <div class="w-10 h-10 rounded-lg bg-slate-50 flex items-center justify-center mb-4 group-hover:bg-blue-50 transition-colors">
             <span class="text-lg font-bold text-slate-400 group-hover:text-blue-600">{{ cat.name.charAt(0) }}</span>
           </div>
           <h3 class="font-bold text-slate-900 truncate">{{ cat.name }}</h3>
           <p class="text-xs text-slate-500 mt-1 truncate">{{ cat.description || '各类工程规格齐全' }}</p>
         </div>
      </div>
    </section>

    <section class="border-t border-gray-200 bg-white py-12">
      <div class="max-w-7xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
        <div class="space-y-1">
          <div class="text-2xl font-black text-slate-900">24h</div>
          <div class="text-xs font-bold text-slate-400 uppercase tracking-widest">全境闪送</div>
        </div>
        <div class="space-y-1">
          <div class="text-2xl font-black text-slate-900">100%</div>
          <div class="text-xs font-bold text-slate-400 uppercase tracking-widest">保检纯铜</div>
        </div>
        <div class="space-y-1">
          <div class="text-2xl font-black text-slate-900">30天</div>
          <div class="text-xs font-bold text-slate-400 uppercase tracking-widest">无忧退换</div>
        </div>
        <div class="space-y-1">
          <div class="text-2xl font-black text-slate-900">账期</div>
          <div class="text-xs font-bold text-slate-400 uppercase tracking-widest">企业级支持</div>
        </div>
      </div>
    </section>

    <SmartInquiryModal :is-open="showSmartInquiry" @close="showSmartInquiry = false" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import SmartInquiryModal from '../components/SmartInquiryModal.vue';
import api from '../api/axios'; // 引入真实 API

const router = useRouter();
const showSmartInquiry = ref(false);
const trackQuery = ref('');
const trackResult = ref('');
const tracking = ref(false);

const categories = ref([]);
const copperPrice = ref({ symbol: '¥', price: 0, updated: '' });

// 1. 获取分类
const fetchCategories = async () => {
  try {
    // 仅获取顶级分类
    const res = await api.get('/categories/');
    categories.value = res.data.filter(c => !c.parent_id);
  } catch (e) {
    console.error('Failed to fetch categories', e);
  }
};

// 2. 获取铜价
const fetchCopperPrice = async () => {
  try {
    const res = await api.get('/meta/prices');
    copperPrice.value = res.data.CNY;
    copperPrice.value.updated = res.data.updated;
  } catch (e) {
    console.error('Failed to fetch copper price', e);
  }
};

// 3. 物流追踪
const quickTrack = async () => {
  if (!trackQuery.value) return;
  
  tracking.value = true;
  trackResult.value = '';
  
  try {
    const res = await api.get(`/orders/track/${trackQuery.value}`);
    const data = res.data;
    trackResult.value = `✅ 订单 #${data.id} [${data.status_text}]\n📦 包含 ${data.item_count} 件商品\n🚚 ${data.driver_info}`;
  } catch (e) {
    trackResult.value = '❌ 未找到该订单信息，请核对单号。';
  } finally {
    tracking.value = false;
  }
};

onMounted(() => {
  fetchCategories();
  fetchCopperPrice();
});
</script>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.3s ease-out forwards;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>