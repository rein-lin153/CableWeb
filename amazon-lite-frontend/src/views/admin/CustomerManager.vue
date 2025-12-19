<template>
  <div class="flex flex-col h-full bg-white rounded-xl shadow-sm border border-gray-100">
    <div class="p-6 border-b border-gray-100 flex justify-between items-center">
      <h2 class="text-xl font-bold text-gray-900 flex items-center">
        <span class="w-2 h-6 bg-blue-500 rounded-full mr-3"></span>
        注册客户列表
      </h2>
      <button @click="openCreateModal" class="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
        + 录入新客户
      </button>
    </div>

    <div class="flex-1 overflow-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50 sticky top-0">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">客户信息</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">折扣率</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">注册时间</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50">
            <td class="px-6 py-4">
              <div class="flex items-center">
                <div class="h-8 w-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold mr-2">
                  {{ (user.username || user.email).charAt(0).toUpperCase() }}
                </div>
                <div>
                  <div class="text-sm font-bold text-gray-900">{{ user.username || '未命名' }}</div>
                  <div class="text-xs text-gray-500">{{ user.email }}</div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 text-sm text-gray-600">
              <span v-if="user.discount_rate > 0" class="text-orange-600 font-bold">{{ (user.discount_rate * 100).toFixed(0) }}% OFF</span>
              <span v-else class="text-gray-400">无折扣</span>
            </td>
            <td class="px-6 py-4">
              <button @click="toggleStatus(user)" class="px-2 py-1 text-xs rounded" :class="user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
                {{ user.is_active ? '正常' : '封禁' }}
              </button>
            </td>
            <td class="px-6 py-4 text-sm text-gray-500">{{ new Date(user.created_at).toLocaleDateString() }}</td>
            <td class="px-6 py-4 text-right space-x-2 text-sm">
              <button @click="openDiscountModal(user)" class="text-indigo-600 hover:underline">设折扣</button>
              <button @click="handleDelete(user)" class="text-red-600 hover:underline">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white p-6 rounded-xl shadow-xl w-96">
        <h3 class="font-bold mb-4">录入新客户</h3>
        <form @submit.prevent="handleSubmit" class="space-y-3">
          <input v-model="form.username" placeholder="客户姓名" class="w-full border p-2 rounded" required>
          <input v-model="form.email" type="email" placeholder="邮箱" class="w-full border p-2 rounded" required>
          <input v-model="form.password" type="password" placeholder="初始密码" class="w-full border p-2 rounded" required>
          <div class="flex justify-end gap-2 mt-4">
            <button type="button" @click="showModal = false" class="px-4 py-2 text-gray-600">取消</button>
            <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded">确认录入</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="editingUser" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="bg-white p-6 rounded-xl shadow-xl w-80">
        <h3 class="font-bold mb-4">设置折扣</h3>
        <input v-model.number="discountRate" type="number" step="0.01" max="1" placeholder="0.05 代表 5% OFF" class="w-full border p-2 rounded mb-4">
        <div class="flex justify-end gap-2">
          <button @click="editingUser = null" class="px-4 py-2 text-gray-600">取消</button>
          <button @click="submitDiscount" class="px-4 py-2 bg-indigo-600 text-white rounded">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import api from '../../api/axios';

const users = ref([]);
const showModal = ref(false);
const editingUser = ref(null);
const discountRate = ref(0);
const form = reactive({ username: '', email: '', password: '' });

// 获取所有用户，并在前端过滤 role='user'
const fetchCustomers = async () => {
  try {
    const res = await api.get('/users/?limit=200');
    // 【核心逻辑】只保留普通用户
    users.value = res.data.filter(u => u.role === 'user' || !u.role);
  } catch (e) { console.error(e); }
};

const toggleStatus = async (user) => {
  try { await api.patch(`/users/${user.id}/status`, { is_active: !user.is_active }); user.is_active = !user.is_active; } catch (e) { alert('失败'); }
};

const handleDelete = async (user) => {
  if(!confirm('确定删除此客户吗？')) return;
  try { await api.delete(`/users/${user.id}`); fetchCustomers(); } catch (e) { alert('失败'); }
};

// 新增客户
const openCreateModal = () => { Object.assign(form, { username: '', email: '', password: '' }); showModal.value = true; };
const handleSubmit = async () => {
  try {
    // 强制 role = user
    await api.post('/users/', { ...form, role: 'user' });
    showModal.value = false;
    fetchCustomers();
    alert('客户录入成功');
  } catch (e) { alert('录入失败'); }
};

// 折扣
const openDiscountModal = (user) => { editingUser.value = user; discountRate.value = user.discount_rate || 0; };
const submitDiscount = async () => {
  try {
    await api.patch(`/users/${editingUser.value.id}/discount`, { discount_rate: discountRate.value });
    editingUser.value = null;
    fetchCustomers();
  } catch (e) { alert('设置失败'); }
};

onMounted(fetchCustomers);
</script>