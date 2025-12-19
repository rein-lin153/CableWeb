<template>
  <div class="min-h-screen bg-gray-50 pt-20 pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <div class="text-center mb-12">
        <h1 class="text-3xl font-extrabold text-gray-900 sm:text-4xl">
          纯国标 · 真品质
        </h1>
        <p class="mt-4 text-lg text-gray-500">
          我们承诺每一米电线都经过严格检测，核心指标全面优于国家标准 (GB/T 5023.3-2008)。
        </p>
      </div>

      <div class="mb-8 flex flex-col sm:flex-row justify-between items-center gap-4 bg-white p-4 rounded-xl shadow-sm border border-gray-100">
        <div class="flex space-x-2">
          <button 
            v-for="cat in categories" 
            :key="cat"
            @click="currentCategory = cat"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            :class="currentCategory === cat ? 'bg-orange-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
          >
            {{ cat }}
          </button>
        </div>

        <div class="relative w-full sm:w-64">
          <input 
            v-model="searchQuery"
            type="text" 
            placeholder="搜索型号 (如 BVR 2.5)"
            class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
          <svg class="w-5 h-5 text-gray-400 absolute left-3 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
        </div>
      </div>

      <div v-if="loading" class="text-center py-20 text-gray-500">加载中...</div>
      
      <div v-else class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div v-for="spec in filteredSpecs" :key="spec.id" class="bg-white rounded-2xl shadow-sm hover:shadow-xl transition-shadow duration-300 overflow-hidden border border-gray-100 group">
          
          <div class="bg-gray-900 px-6 py-4 flex justify-between items-center">
            <div>
              <span class="text-xs font-bold text-orange-400 bg-orange-900/30 px-2 py-1 rounded mb-1 inline-block">{{ spec.category }}</span>
              <h3 class="text-xl font-bold text-white">{{ spec.model }}</h3>
            </div>
            <svg class="w-8 h-8 text-gray-700 group-hover:text-orange-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </div>

          <div class="p-6">
            <div class="space-y-4">
              
              <div>
                <p class="text-xs text-gray-400 uppercase tracking-wider">国家标准 (GB)</p>
                <p class="text-sm font-medium text-gray-600 mt-1">{{ spec.standard_param }}</p>
              </div>

              <div class="h-px bg-gray-100"></div>

              <div>
                <p class="text-xs text-orange-600 uppercase tracking-wider font-bold">我们实测数据</p>
                <div class="flex items-center mt-1">
                  <p class="text-lg font-bold text-gray-900">{{ spec.actual_param }}</p>
                  <span class="ml-2 px-2 py-0.5 bg-green-100 text-green-700 text-xs font-bold rounded-full">合格</span>
                </div>
              </div>

              <div class="pt-4 mt-2 bg-gray-50 -mx-6 -mb-6 px-6 py-3 border-t border-gray-100">
                <p class="text-xs text-gray-500">
                  <span class="font-bold">特性：</span> {{ spec.feature }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../api/axios';

const specs = ref([]);
const loading = ref(true);
const currentCategory = ref('全部');
const searchQuery = ref('');

// 硬编码分类，或者也可以从后端获取
const categories = ['全部', '家装电线', '工程电缆', '特种线缆'];

// 获取数据
const fetchSpecs = async () => {
  loading.value = true;
  try {
    // 确保路径和后端定义的 API 一致
    // 如果你在 axios.js 里配置了 baseURL: '.../api/v1'，这里写 '/specs/' 即可
    const res = await api.get('/specs/'); 
    specs.value = res.data;
  } catch (e) {
    console.error("获取参数失败", e);
    // ✅ 删掉这里原有的 specs.value = [...] 模拟数据
    // 改为报错提示，这样你就知道接口通没通了
    alert('无法连接到后端参数接口，请检查后端服务');
  } finally {
    loading.value = false;
  }
};

// 过滤逻辑
const filteredSpecs = computed(() => {
  return specs.value.filter(s => {
    const matchCat = currentCategory.value === '全部' || s.category === currentCategory.value;
    const matchSearch = s.model.toLowerCase().includes(searchQuery.value.toLowerCase());
    return matchCat && matchSearch;
  });
});

onMounted(fetchSpecs);
</script>