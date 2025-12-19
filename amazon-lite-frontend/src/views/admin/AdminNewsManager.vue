<template>
  <div class="flex flex-col h-full bg-white rounded-xl shadow-sm border border-gray-100">
    
    <div class="p-6 border-b border-gray-100 flex justify-between items-center">
      <h2 class="text-xl font-bold text-gray-900 flex items-center">
        <span class="w-2 h-6 bg-indigo-500 rounded-full mr-3"></span>
        新闻资讯管理
      </h2>
      <button @click="openModal" class="bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-orange-600 transition-colors flex items-center">
        <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
        发布新闻
      </button>
    </div>

    <div class="flex-1 overflow-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">封面图</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">标题 / 摘要</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">发布时间</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="item in newsList" :key="item.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">
              <img :src="item.image_url" class="h-16 w-24 object-cover rounded-md bg-gray-100 border border-gray-200">
            </td>
            <td class="px-6 py-4">
              <div class="text-sm font-bold text-gray-900 line-clamp-1">{{ item.title }}</div>
              <div class="text-xs text-gray-500 mt-1 line-clamp-2 w-64">{{ item.summary }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ new Date(item.created_at).toLocaleDateString() }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button @click="handleDelete(item)" class="text-red-600 hover:text-red-900">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="newsList.length === 0" class="p-10 text-center text-gray-400 text-sm">暂无新闻数据</div>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-900 bg-opacity-75 transition-opacity" @click="showModal = false"></div>
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6">
            <h3 class="text-lg font-bold text-gray-900 mb-4">发布新资讯</h3>
            <form @submit.prevent="handleSubmit" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">新闻标题</label>
                <input v-model="form.title" required type="text" class="w-full border border-gray-300 rounded-md py-2 px-3 text-sm focus:ring-indigo-500 focus:border-indigo-500">
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">封面图片 URL</label>
                <input v-model="form.image_url" required type="url" placeholder="https://..." class="w-full border border-gray-300 rounded-md py-2 px-3 text-sm focus:ring-indigo-500 focus:border-indigo-500">
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">简短摘要</label>
                <textarea v-model="form.summary" required rows="2" class="w-full border border-gray-300 rounded-md py-2 px-3 text-sm focus:ring-indigo-500 focus:border-indigo-500"></textarea>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">详细内容</label>
                <textarea v-model="form.content" required rows="5" class="w-full border border-gray-300 rounded-md py-2 px-3 text-sm focus:ring-indigo-500 focus:border-indigo-500"></textarea>
              </div>
              <div class="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
                <button type="submit" :disabled="submitting" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-gray-900 text-base font-medium text-white hover:bg-orange-600 sm:col-start-2 sm:text-sm">
                  {{ submitting ? '发布中...' : '确认发布' }}
                </button>
                <button type="button" @click="showModal = false" class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 sm:mt-0 sm:col-start-1 sm:text-sm">
                  取消
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import api from '../../api/axios';

const newsList = ref([]);
const showModal = ref(false);
const submitting = ref(false);
const form = reactive({ title: '', summary: '', content: '', image_url: '' });

const fetchNews = async () => {
  try {
    const res = await api.get('/news/');
    newsList.value = res.data;
  } catch (e) { console.error(e); }
};

const openModal = () => {
  Object.assign(form, { title: '', summary: '', content: '', image_url: '' });
  showModal.value = true;
};

const handleSubmit = async () => {
  submitting.value = true;
  try {
    await api.post('/news/', form);
    showModal.value = false;
    fetchNews();
    alert('发布成功');
  } catch (e) {
    alert('发布失败');
  } finally {
    submitting.value = false;
  }
};

const handleDelete = async (item) => {
  if (!confirm('确定删除这条新闻吗？')) return;
  try {
    await api.delete(`/news/${item.id}`);
    fetchNews();
  } catch (e) { alert('删除失败'); }
};

onMounted(fetchNews);
</script>