<template>
  <div class="bg-gray-50 min-h-screen pt-24 pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <div class="mb-12 text-center animate-fade-in-down">
        <h1 class="text-3xl font-bold text-gray-900">企业新闻中心</h1>
        <p class="text-gray-500 mt-2">了解 Amazon Cable 的最新动态、技术突破与行业见解</p>
      </div>

      <div v-if="loading" class="py-20 text-center">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-orange-500 mx-auto"></div>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <article 
          v-for="(news, index) in sortedNewsList" 
          :key="news.id"
          @click="$router.push(`/news/${news.id}`)"
          class="bg-white rounded-2xl overflow-hidden hover:shadow-xl transition-all duration-300 cursor-pointer group flex flex-col animate-fade-in-up"
          :style="{ animationDelay: `${index * 100}ms` }"
        >
          <div class="aspect-video bg-gray-100 overflow-hidden relative">
            <img 
              :src="news.image_url" 
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
            >
            <div class="absolute top-4 left-4 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-lg text-xs font-bold text-gray-800 shadow-sm">
              {{ formatDate(news.created_at) }}
            </div>
          </div>

          <div class="p-6 flex flex-col flex-grow">
            <h2 class="text-xl font-bold text-gray-900 mb-3 group-hover:text-orange-600 transition-colors line-clamp-2">
              {{ news.title }}
            </h2>
            <p class="text-gray-500 text-sm line-clamp-3 mb-6 flex-grow leading-relaxed">
              {{ news.summary }}
            </p>
            
            <div class="pt-4 border-t border-gray-50 flex justify-between items-center mt-auto">
              <span class="text-xs text-gray-400">By Admin</span>
              <span class="text-sm font-bold text-orange-600 flex items-center group-hover:translate-x-1 transition-transform">
                阅读全文 <svg class="w-4 h-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" /></svg>
              </span>
            </div>
          </div>
        </article>
      </div>

      <div v-if="!loading && newsList.length === 0" class="text-center py-20 text-gray-400">
        暂无发布的新闻
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../api/axios';

const newsList = ref([]);
const loading = ref(true);

const fetchAllNews = async () => {
  loading.value = true;
  try {
    // 获取足够多的新闻
    const res = await api.get('/news/?limit=100');
    newsList.value = res.data;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// 排序逻辑
const sortedNewsList = computed(() => {
  // 创建一个副本进行排序，不影响原数据
  return [...newsList.value].sort((a, b) => {
    // 【修改这里】
    // new Date(b.created_at) - new Date(a.created_at)  => 倒序 (最新的在前面) -> 推荐
    // new Date(a.created_at) - new Date(b.created_at)  => 正序 (最旧的在前面)
    
    return new Date(b.created_at) - new Date(a.created_at); 
  });
});

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit'
  });
};

onMounted(() => {
  fetchAllNews();
});
</script>

<style scoped>
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeInDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }

.animate-fade-in-up { animation: fadeInUp 0.6s ease-out forwards; opacity: 0; }
.animate-fade-in-down { animation: fadeInDown 0.6s ease-out forwards; }
</style>