<template>
  <div class="min-h-screen bg-slate-900 text-slate-200 p-4 pt-24">
    <div class="max-w-md mx-auto bg-slate-800 rounded-2xl shadow-xl overflow-hidden border border-slate-700">
      
      <div class="bg-gradient-to-r from-purple-600 to-purple-800 p-6 relative overflow-hidden">
        <div class="absolute -right-6 -top-6 w-24 h-24 bg-white/10 rounded-full blur-2xl"></div>
        <h2 class="text-xl font-bold text-white flex items-center">
          <svg class="w-6 h-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" /></svg>
          线规对照换算
        </h2>
        <p class="text-purple-200 text-xs mt-1">AWG vs Metric (mm²) Converter</p>
      </div>

      <div class="p-6 space-y-6">
        
        <div class="flex bg-slate-900 p-1 rounded-lg border border-slate-600">
          <button @click="mode = 'awg_to_mm'" :class="mode === 'awg_to_mm' ? 'bg-purple-600 text-white shadow' : 'text-slate-400 hover:text-white'" class="flex-1 py-2 rounded text-xs font-bold transition-all">
            美标 AWG <span class="mx-1">→</span> 国标 mm²
          </button>
          <button @click="mode = 'mm_to_awg'" :class="mode === 'mm_to_awg' ? 'bg-purple-600 text-white shadow' : 'text-slate-400 hover:text-white'" class="flex-1 py-2 rounded text-xs font-bold transition-all">
            国标 mm² <span class="mx-1">→</span> 美标 AWG
          </button>
        </div>

        <div v-if="mode === 'awg_to_mm'" class="space-y-4 animate-fade-in">
           <label class="text-xs font-bold text-slate-400 uppercase tracking-wider block">选择 AWG 规格</label>
           <select v-model="selectedAwg" class="w-full bg-slate-900 border border-slate-600 rounded p-3 text-white focus:border-purple-500 outline-none font-mono">
             <option v-for="(data, key) in awgData" :key="key" :value="key">{{ key }} ({{ data.dia }}mm)</option>
           </select>
        </div>

        <div v-else class="space-y-4 animate-fade-in">
           <label class="text-xs font-bold text-slate-400 uppercase tracking-wider block">选择国标截面</label>
           <select v-model="selectedMm" class="w-full bg-slate-900 border border-slate-600 rounded p-3 text-white focus:border-purple-500 outline-none font-mono">
             <option v-for="size in mmSizes" :key="size" :value="size">{{ size }} mm²</option>
           </select>
        </div>

        <div class="bg-slate-900 rounded-xl p-6 border border-slate-700 relative overflow-hidden">
           <div class="absolute top-0 right-0 p-4 opacity-10">
             <svg class="w-24 h-24 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
           </div>
           
           <div class="relative z-10 text-center">
             <p class="text-slate-400 text-xs uppercase mb-2">Equivalent Standard / 等效规格</p>
             <div class="text-4xl font-black text-white font-mono tracking-tight">
               {{ resultData.main }}
             </div>
             <div class="text-purple-400 text-sm font-bold mt-1">
               {{ resultData.sub }}
             </div>
           </div>

           <div class="grid grid-cols-2 gap-4 mt-6 pt-6 border-t border-slate-800">
             <div class="text-center">
               <div class="text-xs text-slate-500">近似直径</div>
               <div class="text-slate-300 font-mono">{{ resultData.diameter }} mm</div>
             </div>
             <div class="text-center">
               <div class="text-xs text-slate-500">参考载流 (Air)</div>
               <div class="text-slate-300 font-mono text-emerald-400">{{ resultData.amp }} A</div>
             </div>
           </div>
        </div>

        <div class="bg-purple-900/20 border border-purple-500/30 p-4 rounded-lg flex items-start gap-3">
           <svg class="w-5 h-5 text-purple-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
           <div>
             <h4 class="text-sm font-bold text-purple-200">采购建议</h4>
             <p class="text-xs text-purple-300/80 mt-1 leading-relaxed">
               {{ resultData.advice }}
             </p>
           </div>
        </div>

        <button @click="$router.push(`/products?q=${encodeURIComponent(resultData.searchKey)}`)" class="w-full py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-lg font-bold shadow-lg shadow-purple-900/50 transition-all mt-2">
          查找 {{ resultData.searchKey }} 现货
        </button>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const mode = ref('awg_to_mm');
const selectedAwg = ref('12 AWG');
const selectedMm = ref(4);

// 简化的数据映射表
const awgData = {
  '18 AWG': { mm: 0.82, dia: 1.02, amp: 10, equiv: '0.75 mm²' },
  '16 AWG': { mm: 1.31, dia: 1.29, amp: 15, equiv: '1.5 mm²' },
  '14 AWG': { mm: 2.08, dia: 1.63, amp: 20, equiv: '2.5 mm²' },
  '12 AWG': { mm: 3.31, dia: 2.05, amp: 25, equiv: '4 mm²' },
  '10 AWG': { mm: 5.26, dia: 2.59, amp: 35, equiv: '6 mm²' },
  '8 AWG':  { mm: 8.37, dia: 3.26, amp: 50, equiv: '10 mm²' },
  '6 AWG':  { mm: 13.3, dia: 4.11, amp: 65, equiv: '16 mm²' },
  '4 AWG':  { mm: 21.2, dia: 5.19, amp: 85, equiv: '25 mm²' },
  '2 AWG':  { mm: 33.6, dia: 6.54, amp: 115, equiv: '35 mm²' },
  '1/0 AWG':{ mm: 53.5, dia: 8.25, amp: 150, equiv: '50 mm²' },
  '2/0 AWG':{ mm: 67.4, dia: 9.27, amp: 175, equiv: '70 mm²' },
  '4/0 AWG':{ mm: 107,  dia: 11.7, amp: 230, equiv: '120 mm²' },
};

const mmSizes = [0.75, 1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120];

const resultData = computed(() => {
  if (mode.value === 'awg_to_mm') {
    const data = awgData[selectedAwg.value];
    return {
      main: data.equiv,
      sub: `Exact: ${data.mm} mm²`,
      diameter: data.dia,
      amp: data.amp,
      searchKey: data.equiv.split(' ')[0], // '4' from '4 mm²'
      advice: `美标 ${selectedAwg.value} 对应国标最接近规格为 ${data.equiv}。通常可直接替代。`
    };
  } else {
    // 简单的反向查找逻辑 (Find closest)
    let bestAwg = '12 AWG';
    let minDiff = 999;
    
    for (const [key, val] of Object.entries(awgData)) {
      const diff = Math.abs(val.mm - selectedMm.value);
      if (diff < minDiff) {
        minDiff = diff;
        bestAwg = key;
      }
    }
    const data = awgData[bestAwg];
    return {
      main: bestAwg,
      sub: `~ ${selectedMm.value} mm²`,
      diameter: data.dia,
      amp: data.amp,
      searchKey: selectedMm.value,
      advice: `国标 ${selectedMm.value}mm² 约等于美标 ${bestAwg}。如需出口设备配套，请选用此规格。`
    };
  }
});
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>