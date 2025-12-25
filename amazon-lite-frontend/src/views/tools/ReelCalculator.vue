<template>
  <div class="min-h-screen bg-slate-900 text-slate-200 p-4 pt-24">
    <div class="max-w-md mx-auto bg-slate-800 rounded-2xl shadow-xl overflow-hidden border border-slate-700">
      
      <div class="bg-gradient-to-r from-cyan-600 to-cyan-800 p-6 relative overflow-hidden">
        <div class="absolute -right-6 -top-6 w-24 h-24 bg-white/10 rounded-full blur-2xl"></div>
        <h2 class="text-xl font-bold text-white flex items-center">
          <svg class="w-6 h-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          智能装盘计算
        </h2>
        <p class="text-cyan-200 text-xs mt-1">Cable Reel & Logistics Calculator</p>
      </div>

      <div class="p-6 space-y-6">
        
        <div class="space-y-4">
           <div>
             <label class="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">电缆外径 (Diameter)</label>
             <div class="relative">
               <input v-model.number="cableDia" type="number" class="w-full bg-slate-900 border border-slate-600 rounded p-3 text-white focus:border-cyan-500 outline-none font-mono">
               <span class="absolute right-3 top-3 text-slate-500 font-bold">mm</span>
             </div>
           </div>
           
           <div>
             <label class="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">采购长度 (Length)</label>
             <div class="relative">
               <input v-model.number="cableLen" type="number" class="w-full bg-slate-900 border border-slate-600 rounded p-3 text-white focus:border-cyan-500 outline-none font-mono">
               <span class="absolute right-3 top-3 text-slate-500 font-bold">m</span>
             </div>
           </div>
        </div>

        <div class="bg-slate-900 rounded-xl p-6 border border-slate-700 text-center relative overflow-hidden">
           
           <div v-if="recommendedReel" class="relative z-10">
              <div class="w-32 h-32 mx-auto border-4 border-cyan-600 rounded-full flex items-center justify-center relative bg-cyan-900/20">
                 <div class="w-16 h-16 border-2 border-dashed border-cyan-400/50 rounded-full absolute"></div>
                 <div class="text-cyan-400 font-black text-xl">PN {{ recommendedReel.type }}</div>
              </div>
              
              <div class="mt-4 grid grid-cols-2 gap-4 text-left">
                <div>
                   <div class="text-[10px] text-slate-500 uppercase">盘具尺寸 (HxW)</div>
                   <div class="text-sm font-mono text-white">{{ recommendedReel.flange }} x {{ recommendedReel.width }} mm</div>
                </div>
                <div>
                   <div class="text-[10px] text-slate-500 uppercase">预估总重</div>
                   <div class="text-sm font-mono text-white">~{{ totalWeight }} kg</div>
                </div>
                <div>
                   <div class="text-[10px] text-slate-500 uppercase">物流建议</div>
                   <div class="text-sm font-bold text-cyan-400">{{ recommendedReel.truck }}</div>
                </div>
              </div>
           </div>

           <div v-else class="text-red-400 text-sm py-4">
              无合适标准盘具，建议分盘运输。
           </div>
        </div>

        <button @click="$router.push('/products')" class="w-full py-3 bg-slate-700 hover:bg-cyan-600 text-white rounded-lg font-bold transition-all border border-slate-600 hover:border-cyan-500">
          联系客服安排分盘
        </button>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const cableDia = ref(25); // mm
const cableLen = ref(500); // m

// 标准木盘/铁盘数据 (Simplified GB/T)
const reels = [
  { type: '800',  flange: 800,  barrel: 400,  width: 500,  weight: 60,   truck: '微卡/皮卡' },
  { type: '1000', flange: 1000, barrel: 500,  width: 600,  weight: 90,   truck: '4.2米货车' },
  { type: '1250', flange: 1250, barrel: 630,  width: 700,  weight: 150,  truck: '4.2米货车' },
  { type: '1600', flange: 1600, barrel: 800,  width: 900,  weight: 280,  truck: '6.8米货车' },
  { type: '2000', flange: 2000, barrel: 1000, width: 1100, weight: 450,  truck: '9.6米/吊车' },
  { type: '2500', flange: 2500, barrel: 1250, width: 1300, weight: 800,  truck: '13米半挂' },
];

const recommendedReel = computed(() => {
  const d = cableDia.value;
  const L = cableLen.value;
  
  // 估算装盘长度公式: L = π * n * (D_avg) 
  // 简化体积法: CableVol = L * (d^2) * 1.1 (间隙系数)
  // ReelVol = Width * pi * ((Flange/2)^2 - (Barrel/2)^2) * 0.85 (填充率)
  
  for (const reel of reels) {
    const volAvailable = reel.width * Math.PI * (Math.pow(reel.flange/2, 2) - Math.pow(reel.barrel/2, 2)) * 0.85;
    const volNeeded = L * Math.pow(d, 2) * 1.1; // 简化为方体堆积估算
    
    // 还需要检查弯曲半径：桶径应 > 15倍电缆外径
    const bendingOk = reel.barrel > (15 * d);

    if (volAvailable > volNeeded && bendingOk) {
      return reel;
    }
  }
  return null;
});

const totalWeight = computed(() => {
  // 粗略估算电缆重量: 铜密度8.9 + 绝缘
  // 简化经验公式: kg/m ≈ 0.01 * d^2 (非常粗略)
  const cableWeight = cableLen.value * (0.008 * Math.pow(cableDia.value, 2)); 
  const reelWeight = recommendedReel.value ? recommendedReel.value.weight : 0;
  return Math.round(cableWeight + reelWeight);
});
</script>