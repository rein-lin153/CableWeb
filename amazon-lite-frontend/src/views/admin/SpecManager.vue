<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">国标参数管理</h1>
      <button @click="openModal()" class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 font-bold flex items-center">
        <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
        添加新规格
      </button>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">型号</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">分类</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">国标值 vs 实测值</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="item in specs" :key="item.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap font-bold text-gray-900">{{ item.model }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ item.category }}</td>
            <td class="px-6 py-4 text-sm">
              <div class="text-gray-500 text-xs">标: {{ item.standard_param }}</div>
              <div class="text-green-600 font-bold">实: {{ item.actual_param }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button @click="openModal(item)" class="text-indigo-600 hover:text-indigo-900 mr-4">编辑</button>
              <button @click="deleteSpec(item.id)" class="text-red-600 hover:text-red-900">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">{{ isEditing ? '编辑参数' : '添加新规格' }}</h2>
        
        <form @submit.prevent="submitForm" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">规格型号</label>
            <input v-model="form.model" type="text" class="mt-1 w-full border rounded p-2" required placeholder="例如: BVR 2.5">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">分类</label>
            <select v-model="form.category" class="mt-1 w-full border rounded p-2">
              <option>家装电线</option>
              <option>工程电缆</option>
              <option>特种线缆</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">国家标准要求</label>
            <input v-model="form.standard_param" type="text" class="mt-1 w-full border rounded p-2" placeholder="≤ 7.41Ω/km">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">我司实测数据</label>
            <input v-model="form.actual_param" type="text" class="mt-1 w-full border rounded p-2" placeholder="7.20Ω/km">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">产品特性描述</label>
            <input v-model="form.feature" type="text" class="mt-1 w-full border rounded p-2">
          </div>

          <div class="flex justify-end space-x-3 mt-6">
            <button type="button" @click="showModal = false" class="px-4 py-2 border rounded text-gray-600 hover:bg-gray-50">取消</button>
            <button type="submit" class="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../api/axios';

const specs = ref([]);
const showModal = ref(false);
const isEditing = ref(false);
const form = ref({ model: '', category: '家装电线', standard_param: '', actual_param: '', feature: '' });
const editId = ref(null);

const fetchSpecs = async () => {
  try {
    const res = await api.get('/specs/');
    specs.value = res.data;
  } catch (e) { console.error(e); }
};

const openModal = (item = null) => {
  if (item) {
    isEditing.value = true;
    editId.value = item.id;
    form.value = { ...item };
  } else {
    isEditing.value = false;
    form.value = { model: '', category: '家装电线', standard_param: '', actual_param: '', feature: '' };
  }
  showModal.value = true;
};

const submitForm = async () => {
  try {
    if (isEditing.value) {
      await api.put(`/specs/${editId.value}`, form.value);
    } else {
      await api.post('/specs/', form.value);
    }
    showModal.value = false;
    fetchSpecs();
    alert('操作成功');
  } catch (e) {
    alert('操作失败');
  }
};

const deleteSpec = async (id) => {
  if (!confirm('确定要删除吗？')) return;
  try {
    await api.delete(`/specs/${id}`);
    fetchSpecs();
  } catch (e) { alert('删除失败'); }
};

onMounted(fetchSpecs);
</script>