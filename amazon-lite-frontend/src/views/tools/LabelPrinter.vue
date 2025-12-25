<template>
  <div class="min-h-screen bg-slate-900 text-slate-200 p-4 pt-24">
    <div class="max-w-2xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6">
      
      <div class="bg-slate-800 rounded-2xl p-6 border border-slate-700 shadow-xl">
        <h2 class="text-lg font-bold text-white mb-4 flex items-center">
          <svg class="w-5 h-5 mr-2 text-pink-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" /></svg>
          标签生成器
        </h2>
        
        <div class="space-y-4">
          <div>
            <label class="text-xs text-slate-400 uppercase">回路名称 (Loop Name)</label>
            <input v-model="label.name" type="text" placeholder="例如：1F 厨房动力柜" class="w-full bg-slate-900 border border-slate-600 rounded p-2 text-white mt-1">
          </div>
          <div>
            <label class="text-xs text-slate-400 uppercase">电缆规格 (Spec)</label>
            <input v-model="label.spec" type="text" placeholder="例如：YJV 4*16+1*10" class="w-full bg-slate-900 border border-slate-600 rounded p-2 text-white mt-1">
          </div>
          <div class="grid grid-cols-2 gap-4">
             <div>
                <label class="text-xs text-slate-400 uppercase">起点 (From)</label>
                <input v-model="label.from" type="text" placeholder="1AP1" class="w-full bg-slate-900 border border-slate-600 rounded p-2 text-white mt-1">
             </div>
             <div>
                <label class="text-xs text-slate-400 uppercase">终点 (To)</label>
                <input v-model="label.to" type="text" placeholder="1AL-Kitchen" class="w-full bg-slate-900 border border-slate-600 rounded p-2 text-white mt-1">
             </div>
          </div>
          
          <div class="pt-4">
             <label class="text-xs text-slate-400 uppercase block mb-2">标签颜色</label>
             <div class="flex gap-3">
               <button @click="color='bg-white text-black'" class="w-8 h-8 rounded-full bg-white border-2 border-slate-500"></button>
               <button @click="color='bg-yellow-400 text-black'" class="w-8 h-8 rounded-full bg-yellow-400 border-2 border-slate-500"></button>
               <button @click="color='bg-red-600 text-white'" class="w-8 h-8 rounded-full bg-red-600 border-2 border-slate-500"></button>
             </div>
          </div>
        </div>
      </div>

      <div class="bg-slate-800 rounded-2xl p-6 border border-slate-700 shadow-xl flex flex-col items-center justify-center">
         <h2 class="text-sm font-bold text-slate-500 mb-4 uppercase">打印预览 (50x80mm)</h2>
         
         <div id="print-area" :class="`w-64 h-40 ${color} rounded-lg shadow-lg p-4 relative overflow-hidden flex flex-col justify-between`">
            <div class="absolute top-4 right-4 w-12 h-12 bg-current opacity-20 rounded-sm"></div>
            
            <div>
               <div class="text-[10px] opacity-60 uppercase tracking-widest">Cable ID</div>
               <div class="font-black text-xl leading-none mt-0.5">{{ label.name || 'LOOP NAME' }}</div>
            </div>

            <div class="border-t border-current/20 pt-2 mt-2">
               <div class="flex justify-between items-end">
                  <div class="text-sm font-bold font-mono">{{ label.spec || 'SPEC...' }}</div>
                  <div class="text-[10px] font-bold border border-current px-1 rounded">QC: PASS</div>
               </div>
               <div class="flex justify-between mt-2 text-xs font-mono opacity-80">
                  <span>FR: {{ label.from || '---' }}</span>
                  <span>TO: {{ label.to || '---' }}</span>
               </div>
            </div>
         </div>

         <button @click="print" class="mt-8 px-8 py-2 bg-pink-600 hover:bg-pink-500 text-white font-bold rounded-lg shadow-lg transition-all flex items-center">
            <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" /></svg>
            打印标签
         </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';

const label = reactive({
  name: '',
  spec: '',
  from: '',
  to: ''
});

const color = ref('bg-yellow-400 text-black');

const print = () => {
  window.print();
};
</script>

<style>
@media print {
  body * {
    visibility: hidden;
  }
  #print-area, #print-area * {
    visibility: visible;
  }
  #print-area {
    position: fixed;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%) scale(1.5);
    box-shadow: none !important;
  }
}
</style>