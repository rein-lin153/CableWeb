<template>
  <div class="bg-white min-h-screen pt-10 pb-20">
    
    <div v-if="loading" class="flex flex-col items-center justify-center py-40">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mb-4"></div>
      <p class="text-gray-500">正在加载文章内容...</p>
    </div>

    <div v-else-if="error" class="text-center py-40">
      <h2 class="text-2xl font-bold text-gray-800 mb-2">未找到该新闻</h2>
      <p class="text-gray-500 mb-6">可能文章已被删除或链接无效</p>
      <button @click="$router.push('/')" class="text-orange-600 hover:underline">返回首页</button>
    </div>

    <article v-else class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 animate-fade-in-up">
      
      <header class="mb-8 text-center">
        <div class="inline-block px-3 py-1 mb-4 text-xs font-semibold tracking-wider text-orange-600 uppercase bg-orange-50 rounded-full">
          Amazon Cable News
        </div>
        <h1 class="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 leading-tight mb-6">
          {{ news.title }}
        </h1>
        <div class="flex justify-center items-center text-gray-500 text-sm space-x-4">
          <span class="flex items-center">
            <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
            {{ formatDate(news.created_at) }}
          </span>
          <span class="flex items-center">
            <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
            By Admin
          </span>
        </div>
      </header>

      <figure class="mb-10 rounded-2xl overflow-hidden shadow-lg aspect-video bg-gray-100">
        <img 
          :src="news.image_url" 
          :alt="news.title" 
          class="w-full h-full object-cover"
        >
      </figure>

      <div v-if="news.summary" class="bg-gray-50 border-l-4 border-orange-500 p-6 mb-10 rounded-r-lg italic text-gray-700 text-lg">
        {{ news.summary }}
      </div>

      <div class="prose prose-lg max-w-none text-gray-800 leading-relaxed whitespace-pre-wrap">
        {{ news.content }}
      </div>

      <div class="mt-16 pt-8 border-t border-gray-100 flex justify-between items-center">
        <button @click="$router.push('/')" class="flex items-center text-gray-600 hover:text-orange-600 transition-colors font-medium">
          <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
          返回首页
        </button>
        <div class="flex space-x-4">
           <button class="text-gray-400 hover:text-blue-600"><span class="sr-only">Share</span><svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/></svg></button>
        </div>
      </div>

    </article>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router'; // 引入 route 来获取 URL 参数
import api from '../api/axios';

const route = useRoute();
const news = ref(null);
const loading = ref(true);
const error = ref(false);

const fetchNewsDetail = async () => {
  // 从路由参数中获取 ID (/news/:id)
  const newsId = route.params.id;
  
  loading.value = true;
  try {
    const res = await api.get(`/news/${newsId}`);
    news.value = res.data;
  } catch (err) {
    console.error(err);
    error.value = true;
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

onMounted(() => {
  fetchNewsDetail();
});
</script>

<style scoped>
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in-up {
  animation: fadeInUp 0.6s ease-out forwards;
}
</style>