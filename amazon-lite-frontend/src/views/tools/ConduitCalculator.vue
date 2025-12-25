<template>
  <div class="min-h-screen bg-slate-900 text-slate-200 p-4 pt-24">
    <div class="max-w-md mx-auto bg-slate-800 rounded-2xl shadow-xl overflow-hidden border border-slate-700">
      
      <div class="bg-gradient-to-r from-emerald-600 to-emerald-800 p-6 relative overflow-hidden">
        <div class="absolute -right-6 -top-6 w-24 h-24 bg-white/10 rounded-full blur-2xl"></div>
        <h2 class="text-xl font-bold text-white flex items-center">
          <svg class="w-6 h-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" /></svg>
          穿管/桥架计算器
        </h2>
        <p class="text-emerald-100 text-xs mt-1">Conduit Fill Ratio Calculator</p>
      </div>

      <div class="p-6 space-y-6">
        
        <div class="space-y-3">
          <div class="flex justify-between items-center">
            <label class="text-xs font-bold text-slate-400 uppercase tracking-wider">第一步：选择电缆</label>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <select v-model="cableType" class="bg-slate-900 border border-slate-600 rounded p-2 text-sm text-white focus:border-emerald-500 outline-none">
              <option value="bv">BV 单芯硬线</option>
              <option value="bvr">BVR 软电线</option>
              <option value="yjv">YJV 电缆</option>
            </select>
            <select v-model.number="cableSize" class="bg-slate-900 border border-slate-600 rounded p-2 text-sm text-white focus:border-emerald-500 outline-none">
              <option :value="2.5">2.5 mm²</option>
              <option :value="4">4 mm²</option>
              <option :value="6">6 mm²</option>
              <option :value="10">10 mm²</option>
              <option :value="16">16 mm²</option>
              <option :value="25">25 mm²</option>
              <option :value="35">35 mm²</option>
              <option :value="50">50 mm²</option>
            </select>
          </div>
          <div class="flex items-center bg-slate-900 border border-slate-600 rounded p-2">
            <span class="text-slate-400 text-sm mr-3">根数</span>
            <input v-model.number="cableCount" type="range" min="1" max="50" class="flex-1 accent-emerald-500">
            <span class="text-white font-mono font-bold w-8 text-right">{{ cableCount }}</span>
          </div>
        </div>

        <div class="space-y-3 pt-4 border-t border-slate-700">
           <label class="text-xs font-bold text-slate-400 uppercase tracking-wider block">第二步：选择管径 (PVC/JDG)</label>
           <div class="grid grid-cols-4 gap-2">
             <button v-for="size in conduitSizes" :key="size" 
               @click="selectedConduit = size"
               :class="selectedConduit === size ? 'bg-emerald-600 text-white border-emerald-500' : 'bg-slate-700 text-slate-300 border-slate-600 hover:bg-slate-600'"
               class="py-2 rounded border text-xs font-bold transition-all">
               Φ{{ size }}
             </button>
           </div>
        </div>

        <div class="relative mt-6 flex justify-center">
           <div class="rounded-full border-4 flex items-center justify-center relative transition-all duration-500 bg-slate-800"
                :class="fillRatio > 40 ? 'border-red-500 shadow-[0_0_20px_rgba(239,68,68,0.3)]' : 'border-emerald-500 shadow-[0_0_20px_rgba(16,185,129,0.3)]'"
                style="width: 200px; height: 200px;">
              
              <div class="absolute bottom-0 w-full bg-current transition-all duration-500 opacity-20"
                   :class="fillRatio > 40 ? 'text-red-500' : 'text-emerald-500'"
                   :style="{ height: `${Math.min(fillRatio, 100)}%` }"></div>

              <div class="text-center z-10">
                <div class="text-3xl font-black font-mono" :class="fillRatio > 40 ? 'text-red-500' : 'text-emerald-400'">
                  {{ fillRatio.toFixed(1) }}%
                </div>
                <div class="text-[10px] text-slate-400 uppercase tracking-widest mt-1">Fill Ratio</div>
              </div>
           </div>

           <div class="absolute -bottom-4 bg-slate-900 px-4 py-1 rounded-full border border-slate-600 flex items-center shadow-lg">
              <span v-if="fillRatio <= 40" class="flex items-center text-emerald-500 text-xs font-bold">
                 <span class="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span> 施工轻松
              </span>
              <span v-else-if="fillRatio <= 55" class="flex items-center text-yellow-500 text-xs font-bold">
                 <span class="w-2 h-2 rounded-full bg-yellow-500 mr-2"></span> 穿管困难
              </span>
              <span v-else class="flex items-center text-red-500 text-xs font-bold">
                 <span class="w-2 h-2 rounded-full bg-red-500 mr-2 animate-ping"></span> 无法施工
              </span>
           </div>
        </div>

        <div class="bg-slate-900/50 rounded-lg p-4 text-xs text-slate-400 leading-relaxed border border-slate-700/50">
           <p><span class="text-slate-200 font-bold">工程师建议：</span> 根据 GB 50303 规范，线管内导线总截面积不应超过管内截面积的 <span class="text-emerald-400 font-bold">40%</span>。</p>
           <div v-if="fillRatio > 40" class="mt-2 text-red-400">
             当前管径太小，建议更换为 <span class="font-bold underline cursor-pointer hover:text-red-300" @click="recommendLarger">Φ{{ recommendedSize }}</span> 或以上。
           </div>
        </div>

        <button @click="$router.push('/products')" class="w-full py-3 bg-slate-700 hover:bg-emerald-600 text-white rounded-lg font-bold transition-all mt-2 border border-slate-600 hover:border-emerald-500">
          选购 Φ{{ selectedConduit }} 穿线管配件
        </button>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const cableType = ref('bv');
const cableSize = ref(4);
const cableCount = ref(3);
const selectedConduit = ref(20);

const conduitSizes = [16, 20, 25, 32, 40, 50, 75, 110];

// 简化的电缆外径估算表 (Diameter in mm)
// 实际生产中应从数据库读取真实外径
const cableDiameters = {
  2.5: 3.4,
  4: 4.2,
  6: 4.8,
  10: 6.2,
  16: 8.0,
  25: 10.5,
  35: 12.0,
  50: 14.5
};

const fillRatio = computed(() => {
  const d_cable = cableDiameters[cableSize.value] || 0;
  // 电缆总截面积 = (pi * (d/2)^2) * count
  const area_cable = Math.PI * Math.pow(d_cable / 2, 2) * cableCount.value;
  
  // 管内截面积 (假设壁厚影响已扣除或取近似内径)
  // PVC管通常标的是外径，这里简单估算内径 = 外径 - 2~4mm
  const inner_d = Math.max(0, selectedConduit.value - 3); 
  const area_conduit = Math.PI * Math.pow(inner_d / 2, 2);
  
  if (area_conduit === 0) return 100;
  
  return (area_cable / area_conduit) * 100;
});

const recommendedSize = computed(() => {
  // 简单查找下一个能满足 < 40% 的尺寸
  for (const size of conduitSizes) {
    const inner_d = Math.max(0, size - 3);
    const area_conduit = Math.PI * Math.pow(inner_d / 2, 2);
    const d_cable = cableDiameters[cableSize.value];
    const area_cable = Math.PI * Math.pow(d_cable / 2, 2) * cableCount.value;
    
    if ((area_cable / area_conduit) * 100 <= 40) {
      return size;
    }
  }
  return 110;
});

const recommendLarger = () => {
  selectedConduit.value = recommendedSize.value;
};
</script>