<template>
  <div class="min-h-screen bg-slate-900 text-slate-200 p-4 pt-24">
    <div class="max-w-md mx-auto bg-slate-800 rounded-2xl shadow-xl overflow-hidden border border-slate-700">
      
      <div class="bg-gradient-to-r from-blue-600 to-blue-800 p-6 relative overflow-hidden">
        <div class="absolute -right-6 -top-6 w-24 h-24 bg-white/10 rounded-full blur-2xl"></div>
        <h2 class="text-xl font-bold text-white flex items-center">
          <svg class="w-6 h-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
          电压降计算器
        </h2>
        <p class="text-blue-200 text-xs mt-1">Voltage Drop Calculator (GB/T)</p>
      </div>

      <div class="p-6 space-y-5">
        
        <div class="space-y-4">
          <div>
            <label class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 block">系统电压 (System Voltage)</label>
            <div class="grid grid-cols-2 gap-2">
              <button @click="voltage = 220" :class="voltage === 220 ? 'bg-blue-600 text-white border-blue-500' : 'bg-slate-700 border-slate-600 hover:bg-slate-600'" class="py-2 rounded border text-sm font-bold transition-all">单相 220V</button>
              <button @click="voltage = 380" :class="voltage === 380 ? 'bg-blue-600 text-white border-blue-500' : 'bg-slate-700 border-slate-600 hover:bg-slate-600'" class="py-2 rounded border text-sm font-bold transition-all">三相 380V</button>
            </div>
          </div>

          <div>
            <label class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 block">负载功率 (Power)</label>
            <div class="relative">
              <input v-model.number="power" type="number" class="w-full bg-slate-900 border border-slate-600 rounded p-3 text-white focus:border-blue-500 outline-none font-mono">
              <span class="absolute right-3 top-3 text-slate-500 font-bold">kW</span>
            </div>
          </div>

          <div>
            <label class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 block">线路长度 (Distance)</label>
            <div class="relative">
              <input v-model.number="distance" type="number" class="w-full bg-slate-900 border border-slate-600 rounded p-3 text-white focus:border-blue-500 outline-none font-mono">
              <span class="absolute right-3 top-3 text-slate-500 font-bold">m</span>
            </div>
          </div>

          <div>
             <label class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 block">电缆截面 (Cable Size)</label>
             <select v-model.number="section" class="w-full bg-slate-900 border border-slate-600 rounded p-3 text-white focus:border-blue-500 outline-none font-mono">
               <option v-for="s in sections" :key="s" :value="s">{{ s }} mm²</option>
             </select>
          </div>
          
           <div>
             <label class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 block">材质 (Material)</label>
             <div class="flex gap-4">
               <label class="flex items-center cursor-pointer">
                 <input type="radio" v-model="material" value="cu" class="text-blue-600 bg-slate-900 border-slate-600">
                 <span class="ml-2 text-sm text-slate-300">铜 (Copper)</span>
               </label>
               <label class="flex items-center cursor-pointer">
                 <input type="radio" v-model="material" value="al" class="text-blue-600 bg-slate-900 border-slate-600">
                 <span class="ml-2 text-sm text-slate-300">铝 (Aluminum)</span>
               </label>
             </div>
          </div>
        </div>

        <div class="bg-slate-900 rounded-xl p-5 border border-slate-700 relative overflow-hidden mt-6">
           <div class="flex justify-between items-end mb-2">
             <span class="text-slate-400 text-sm">计算电流 (I)</span>
             <span class="text-white font-mono">{{ current.toFixed(1) }} A</span>
           </div>
           <div class="flex justify-between items-end mb-2">
             <span class="text-slate-400 text-sm">电压降 (ΔU)</span>
             <span class="font-mono" :class="dropPercent > 5 ? 'text-red-500' : 'text-green-500'">
               {{ dropVal.toFixed(1) }}V ({{ dropPercent.toFixed(2) }}%)
             </span>
           </div>
           
           <div class="mt-4 pt-4 border-t border-slate-800">
             <div v-if="dropPercent <= 5" class="flex items-center text-green-500 text-sm font-bold">
               <svg class="w-5 h-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
               符合国标要求 (≤5%)
             </div>
             <div v-else class="flex items-center text-red-500 text-sm font-bold">
               <svg class="w-5 h-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
               压降过大，建议加大线径
             </div>
           </div>
        </div>

        <button @click="$router.push('/products')" class="w-full py-3 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 text-white rounded-lg font-bold shadow-lg shadow-orange-900/50 transition-all mt-4">
          去购买 {{ section }}mm² 电缆
        </button>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const voltage = ref(380);
const power = ref(10); // kW
const distance = ref(50); // m
const section = ref(4); // mm2
const material = ref('cu');

const sections = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240];

// 估算计算逻辑
const current = computed(() => {
  if (voltage.value === 380) {
    return (power.value * 1000) / (Math.sqrt(3) * 380 * 0.85); // cosφ=0.85
  } else {
    return (power.value * 1000) / (220 * 0.85);
  }
});

const dropVal = computed(() => {
  // 简化系数 K: 铜=0.0185, 铝=0.0315
  // ΔU = (K * I * L) / S (单相 * 2, 三相 * 1.732)
  const rho = material.value === 'cu' ? 0.0175 : 0.0283;
  const L = distance.value;
  const S = section.value;
  const I = current.value;
  
  // 考虑线路电抗的简化公式 (纯阻性估算用于一般工程)
  if (voltage.value === 380) {
     return (1.732 * I * rho * L) / S;
  } else {
     return (2 * I * rho * L) / S;
  }
});

const dropPercent = computed(() => {
  return (dropVal.value / voltage.value) * 100;
});
</script>