<template>
  <div class="bg-[#F8FAFC] min-h-screen font-sans text-slate-800">
    
    <section class="relative pt-32 pb-32 px-4 sm:px-6 lg:px-8 overflow-hidden bg-[#0B1120]">
      <div class="absolute top-0 left-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl mix-blend-screen opacity-30 animate-blob"></div>
      <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-orange-600/10 rounded-full blur-3xl mix-blend-screen opacity-30 animate-blob animation-delay-2000"></div>
      <div class="absolute inset-0 bg-[url('/bz1.jpg')] bg-cover bg-center opacity-[0.08] mix-blend-overlay"></div>
      
      <div class="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-[#F8FAFC] to-transparent z-10"></div>

      <div class="relative z-20 max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-16 items-center">
        
        <div class="lg:col-span-7 space-y-8 animate-fade-in-up">
          <div class="inline-flex items-center px-4 py-1.5 rounded-full bg-slate-800/50 border border-slate-700/50 backdrop-blur-md text-orange-400 text-xs font-bold tracking-wide shadow-lg">
            <span class="relative flex h-2 w-2 mr-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-orange-500"></span>
            </span>
            FACTORY DIRECT · 源头工厂直销
          </div>

          <h1 class="text-5xl md:text-7xl font-extrabold tracking-tight text-white leading-[1.1]">
            工程电缆 <br>
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 via-orange-300 to-yellow-200 filter drop-shadow-lg">
              现货次日必达
            </span>
          </h1>

          <p class="text-lg text-slate-400 max-w-xl leading-relaxed border-l-4 border-orange-500/50 pl-4">
            专注 B2B 工程采购 20 年。线上查库存、锁定底价、一键生成合同。
            <br>金边市区自有车队 <span class="text-white font-bold">免费配送</span>，支持货到验货。
          </p>

          <div class="flex flex-col sm:flex-row gap-4 pt-4">
            <button @click="$router.push('/products')" class="group relative px-8 py-4 bg-gradient-to-r from-orange-600 to-orange-500 text-white rounded-xl font-bold text-lg shadow-xl shadow-orange-500/20 hover:shadow-orange-500/40 hover:-translate-y-1 transition-all overflow-hidden">
              <div class="absolute inset-0 bg-white/20 group-hover:translate-x-full transition-transform duration-500 -skew-x-12 -translate-x-full"></div>
              <div class="flex items-center justify-center relative">
                查看实时库存表
                <svg class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" /></svg>
              </div>
            </button>
            <button @click="showSmartInquiry = true" class="px-8 py-4 bg-white/5 hover:bg-white/10 text-white border border-white/20 backdrop-blur-sm rounded-xl font-bold text-lg transition-all flex items-center justify-center hover:border-white/40">
              上传 BOM 清单报价
            </button>
          </div>
        </div>

        <div class="lg:col-span-5 relative animate-fade-in-up" style="animation-delay: 0.1s">
          <div class="absolute -inset-1 bg-gradient-to-r from-orange-500 to-blue-600 rounded-2xl blur opacity-20"></div>
          
          <div class="relative bg-white/90 backdrop-blur-xl border border-white/50 rounded-2xl p-6 shadow-[0_20px_50px_-12px_rgba(0,0,0,0.3)] ring-1 ring-slate-900/5">
            
            <div class="mb-6 pb-6 border-b border-slate-100">
              <div class="flex items-center justify-between mb-4">
                <label class="text-sm font-bold text-slate-800 flex items-center">
                  <div class="w-2 h-6 bg-blue-600 rounded-sm mr-2"></div>
                  货物追踪
                </label>
                <span class="text-[10px] text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">免登录</span>
              </div>
              <div class="relative group">
                <input 
                  v-model="trackQuery" 
                  @keyup.enter="quickTrack" 
                  type="text" 
                  placeholder="输入单号 (如: 8821) 或手机号" 
                  class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-4 pr-24 text-slate-900 font-medium focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 focus:bg-white transition-all outline-none"
                >
                <button 
                  @click="quickTrack" 
                  class="absolute right-2 top-2 bottom-2 bg-slate-900 hover:bg-blue-600 text-white px-4 rounded-lg text-sm font-bold transition-colors shadow-md"
                >
                  查询
                </button>
              </div>
              
              <transition enter-active-class="transition ease-out duration-200" enter-from-class="opacity-0 -translate-y-2" enter-to-class="opacity-100 translate-y-0">
                <div v-if="trackResult" class="mt-3 p-3 bg-green-50 border border-green-200 text-green-700 text-sm rounded-lg flex items-start shadow-sm">
                  <svg class="w-5 h-5 mr-2 flex-shrink-0 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  {{ trackResult }}
                </div>
              </transition>
            </div>

            <div>
              <div class="flex justify-between items-center mb-4">
                <label class="text-sm font-bold text-slate-800 flex items-center">
                  <div class="w-2 h-6 bg-orange-500 rounded-sm mr-2"></div>
                  今日铜价指数
                </label>
                <span class="text-xs text-slate-400">{{ new Date().toLocaleDateString() }}</span>
              </div>
              
              <div class="grid grid-cols-2 gap-3">
                <div class="p-4 bg-gradient-to-br from-slate-50 to-white rounded-xl border border-slate-100 shadow-sm group hover:shadow-md transition-all hover:border-blue-200">
                  <div class="text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">LME 伦敦铜</div>
                  <div class="text-xl font-black text-slate-800 font-mono">$9,120</div>
                  <div class="flex items-center mt-1">
                    <span class="w-1.5 h-1.5 rounded-full bg-green-500 mr-1.5"></span>
                    <span class="text-xs font-bold text-green-600">+1.2%</span>
                  </div>
                </div>
                <div class="p-4 bg-gradient-to-br from-orange-50/50 to-white rounded-xl border border-orange-100 shadow-sm group hover:shadow-md transition-all hover:border-orange-200">
                  <div class="text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">SMM 长江现货</div>
                  <div class="text-xl font-black text-orange-600 font-mono">¥72,300</div>
                  <div class="flex items-center mt-1">
                    <span class="w-1.5 h-1.5 rounded-full bg-orange-500 mr-1.5"></span>
                    <span class="text-xs font-bold text-orange-600">+0.5%</span>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </section>

    <section class="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-end mb-10">
        <div>
          <h2 class="text-3xl font-bold text-slate-900">热门工程现货</h2>
          <p class="text-slate-500 mt-2">严格执行 GB/T 国家标准，足米足量</p>
        </div>
        <button @click="$router.push('/products')" class="text-sm font-bold text-blue-600 hover:text-blue-700 flex items-center group">
          全部产品 
          <svg class="w-4 h-4 ml-1 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" /></svg>
        </button>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
         <div v-for="(cat, index) in [
           {name: 'YJV 电力电缆', tag: '工程首选', color: 'blue'},
           {name: 'BV 家装电线', tag: '国标纯铜', color: 'orange'},
           {name: 'RVV 护套线', tag: '柔软耐用', color: 'green'},
           {name: 'BVR 软电线', tag: '电柜专用', color: 'purple'}
         ]" :key="cat.name" 
              @click="$router.push(`/products`)"
              class="group relative bg-white rounded-2xl p-6 border border-slate-100 shadow-[0_2px_10px_-4px_rgba(0,0,0,0.05)] hover:shadow-[0_20px_40px_-12px_rgba(0,0,0,0.1)] hover:-translate-y-1 transition-all duration-300 cursor-pointer overflow-hidden">
           
           <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r" :class="`from-${cat.color}-500 to-${cat.color}-300`"></div>
           
           <div class="flex justify-between items-start mb-6">
             <div class="w-12 h-12 rounded-xl bg-slate-50 flex items-center justify-center group-hover:bg-slate-100 transition-colors">
               <span class="text-2xl font-bold text-slate-300 group-hover:text-slate-600 transition-colors">{{ cat.name.charAt(0) }}</span>
             </div>
             <span class="text-[10px] font-bold px-2 py-1 rounded bg-slate-100 text-slate-500 uppercase tracking-wide group-hover:bg-slate-800 group-hover:text-white transition-colors">Stock</span>
           </div>

           <h3 class="text-lg font-bold text-slate-900 mb-1 group-hover:text-blue-700 transition-colors">{{ cat.name }}</h3>
           <p class="text-xs text-slate-400 font-medium mb-6">{{ cat.tag }}</p>

           <div class="flex items-center justify-between pt-4 border-t border-slate-50">
             <span class="text-xs font-bold text-green-600 flex items-center">
               <span class="w-1.5 h-1.5 rounded-full bg-green-500 mr-1.5"></span>
               现货充足
             </span>
             <svg class="w-5 h-5 text-slate-300 group-hover:text-blue-600 transform group-hover:translate-x-1 transition-all" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
           </div>
         </div>
      </div>
    </section>

    <section class="border-t border-slate-200 bg-white py-12">
      <div class="max-w-7xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
        <div class="space-y-2">
          <div class="text-3xl font-black text-slate-900">24h</div>
          <div class="text-xs font-bold text-slate-400 uppercase tracking-widest">闪电发货</div>
        </div>
        <div class="space-y-2">
          <div class="text-3xl font-black text-slate-900">100%</div>
          <div class="text-xs font-bold text-slate-400 uppercase tracking-widest">国标纯铜</div>
        </div>
        <div class="space-y-2">
          <div class="text-3xl font-black text-slate-900">365</div>
          <div class="text-xs font-bold text-slate-400 uppercase tracking-widest">天无休配送</div>
        </div>
        <div class="space-y-2">
          <div class="text-3xl font-black text-slate-900">0</div>
          <div class="text-xs font-bold text-slate-400 uppercase tracking-widest">中间商差价</div>
        </div>
      </div>
    </section>

    <SmartInquiryModal :is-open="showSmartInquiry" @close="showSmartInquiry = false" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import SmartInquiryModal from '../components/SmartInquiryModal.vue';

const router = useRouter();
const showSmartInquiry = ref(false);
const trackQuery = ref('');
const trackResult = ref('');

const quickTrack = async () => {
  if (!trackQuery.value) return;
  trackResult.value = '正在连接物流系统查询...';
  setTimeout(() => {
    const num = trackQuery.value.replace(/\D/g, '');
    if (num.length > 0) {
      trackResult.value = `订单 #${trackQuery.value}：正在配送中 (司机: 012-***-789)，预计今日 14:00 前送达。`;
    } else {
      trackResult.value = '未找到相关订单，请检查单号或联系客服。';
    }
  }, 800);
};
</script>

<style scoped>
/* 定义更平滑的淡入上浮动画 */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in-up {
  animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
}

/* 斑点呼吸动画 */
@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}
.animate-blob {
  animation: blob 7s infinite;
}
.animation-delay-2000 {
  animation-delay: 2s;
}
</style>