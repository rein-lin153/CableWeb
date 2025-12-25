<template>
  <div class="bg-gray-50 min-h-screen pt-24 pb-12">
    <div class="max-w-4xl mx-auto px-4">
      
      <div class="mb-8">
        <h1 class="text-3xl font-black text-gray-900">⚡ 极速文本下单</h1>
        <p class="text-gray-500 mt-2">直接粘贴 Excel 内容或聊天记录，自动识别型号和数量。</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-8 h-[600px]">
        <div class="flex flex-col h-full bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <label class="text-sm font-bold text-gray-700 mb-2 flex justify-between">
            <span>粘贴区域</span>
            <span class="text-xs font-normal text-gray-400">格式：型号 数量 (如: YJV 4*16 100)</span>
          </label>
          <textarea 
            v-model="rawText"
            @input="parseText"
            class="flex-1 w-full bg-gray-50 border border-gray-200 rounded-lg p-4 text-sm font-mono focus:ring-2 focus:ring-blue-500 outline-none resize-none"
            placeholder="YJV 3*2.5 100米&#10;BV 2.5 红色 5卷&#10;..."
          ></textarea>
          <div class="mt-4 flex justify-between items-center">
             <button @click="rawText=''" class="text-sm text-gray-400 hover:text-gray-600">清空</button>
             <button @click="parseText" class="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg text-sm font-bold hover:bg-blue-200">重新识别</button>
          </div>
        </div>

        <div class="flex flex-col h-full bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div class="bg-gray-50 px-4 py-3 border-b border-gray-200 flex justify-between items-center">
            <span class="font-bold text-gray-900 text-sm">识别结果 ({{ parsedItems.length }})</span>
            <span class="text-xs text-orange-600 bg-orange-50 px-2 py-1 rounded border border-orange-100">仅供参考</span>
          </div>
          
          <div class="flex-1 overflow-y-auto p-2 space-y-2">
             <div v-for="(item, index) in parsedItems" :key="index" 
                  class="flex items-center justify-between p-3 bg-white border border-gray-100 rounded hover:border-blue-300 transition-colors group">
               <div>
                 <div class="font-bold text-gray-800 text-sm">{{ item.code }}</div>
                 <div class="text-xs text-gray-400">{{ item.raw }}</div>
               </div>
               <div class="flex items-center gap-2">
                 <input v-model.number="item.qty" type="number" class="w-16 h-8 text-center border border-gray-200 rounded text-sm focus:border-blue-500 outline-none">
                 <span class="text-xs text-gray-500">m/卷</span>
                 <button @click="removeItem(index)" class="text-gray-300 hover:text-red-500 px-2">×</button>
               </div>
             </div>
             
             <div v-if="parsedItems.length === 0" class="h-full flex flex-col items-center justify-center text-gray-300">
               <svg class="w-12 h-12 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
               <p class="text-sm">等待输入...</p>
             </div>
          </div>

          <div class="p-4 border-t border-gray-100 bg-gray-50">
             <button @click="batchSearch" class="w-full py-3 bg-gray-900 text-white rounded-lg font-bold hover:bg-orange-600 transition-colors shadow-lg">
               批量搜索并添加
             </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const rawText = ref('');
const parsedItems = ref([]);

const parseText = () => {
  const lines = rawText.value.split('\n');
  const results = [];
  
  // 简单的正则匹配：尝试提取 线缆型号 和 数字
  // 匹配逻辑：(YJV|BV|BVR|RVV...)? + 规格 + 数量
  const regex = /([a-zA-Z]+\s*[\d\*\.]+)?.*?(\d+)/;

  lines.forEach(line => {
    if (!line.trim()) return;
    
    // 简单 heuristic: 假设行里有数字，最大的数字可能是数量，剩下的可能是型号
    // 实际生产中这里会接 NLP 或更复杂的正则
    const match = line.match(/([a-zA-Z0-9\*\-\.]+)/g); // 提取所有词
    if (match && match.length >= 2) {
       // 假设最后一个数字是数量
       let qty = 1;
       let codeParts = [];
       
       for (let i = 0; i < match.length; i++) {
         const part = match[i];
         if (i === match.length - 1 && /^\d+$/.test(part)) {
           qty = parseInt(part);
         } else {
           codeParts.push(part);
         }
       }
       
       results.push({
         code: codeParts.join(' '),
         qty: qty,
         raw: line
       });
    }
  });
  
  parsedItems.value = results;
};

const removeItem = (idx) => {
  parsedItems.value.splice(idx, 1);
};

const batchSearch = () => {
  // 这里应该跳转到产品页并带上搜索参数，或者调用 API 批量加入购物车
  // 简化处理：跳转到 Products 并带第一个关键词，提示用户
  if (parsedItems.value.length > 0) {
    const firstItem = parsedItems.value[0].code;
    alert(`正在为您匹配 ${parsedItems.value.length} 个产品... (模拟功能：跳转搜索)`);
    router.push(`/products?q=${encodeURIComponent(firstItem)}`);
  }
};
</script>