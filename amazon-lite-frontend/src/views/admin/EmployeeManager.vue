<template>
  <div class="flex flex-col h-full bg-white rounded-xl shadow-sm border border-gray-100">
    <div class="p-6 border-b border-gray-100 flex justify-between items-center">
      <h2 class="text-xl font-bold text-gray-900 flex items-center">
        <span class="w-2 h-6 bg-purple-600 rounded-full mr-3"></span>
        内部员工管理
      </h2>
      <button @click="openCreateModal" class="bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-purple-700 transition-colors flex items-center">
        <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" /></svg>
        新增员工
      </button>
    </div>

    <div class="flex-1 overflow-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">员工姓名</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">登录账号</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">岗位角色</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">入职时间</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50">
            <td class="px-6 py-4">
              <div class="flex items-center">
                <div class="h-8 w-8 rounded-full flex items-center justify-center text-white font-bold mr-3 text-xs"
                     :class="user.role === 'admin' ? 'bg-purple-500' : 'bg-indigo-500'">
                  {{ (user.username || user.email).charAt(0).toUpperCase() }}
                </div>
                <span class="font-bold text-gray-900">{{ user.username }}</span>
              </div>
            </td>
            <td class="px-6 py-4 text-sm text-gray-600 font-mono">{{ user.email }}</td>
            <td class="px-6 py-4">
              <span class="px-2 py-1 rounded text-xs font-bold border" 
                :class="user.role === 'admin' ? 'bg-purple-50 text-purple-700 border-purple-100' : 'bg-indigo-50 text-indigo-700 border-indigo-100'">
                {{ user.role === 'admin' ? '管理员' : '派送员' }}
              </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-500">{{ new Date(user.created_at).toLocaleDateString() }}</td>
            <td class="px-6 py-4 text-right space-x-2 text-sm">
              <button @click="openEditModal(user)" class="text-blue-600 hover:underline">调岗</button>
              <button @click="handleDelete(user)" class="text-red-600 hover:underline" :disabled="user.is_superuser">离职</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white p-6 rounded-xl shadow-xl w-96">
        <h3 class="font-bold mb-4">{{ editingId ? '编辑员工信息' : '录入新员工' }}</h3>
        
        <div class="space-y-3">
          <div>
            <label class="text-xs font-bold text-gray-500">姓名</label>
            <input v-model="form.username" class="w-full border p-2 rounded mt-1">
          </div>
          <div>
            <label class="text-xs font-bold text-gray-500">邮箱 (账号)</label>
            <input v-model="form.email" type="email" :disabled="!!editingId" class="w-full border p-2 rounded mt-1 disabled:bg-gray-100">
          </div>
          <div v-if="!editingId">
            <label class="text-xs font-bold text-gray-500">密码</label>
            <input v-model="form.password" type="password" class="w-full border p-2 rounded mt-1">
          </div>
          <div>
            <label class="text-xs font-bold text-gray-500">岗位</label>
            <select v-model="form.role" class="w-full border p-2 rounded mt-1 bg-white">
              <option value="driver">🚚 派送员</option>
              <option value="admin">🔧 管理员</option>
            </select>
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-6">
          <button @click="showModal = false" class="px-4 py-2 text-gray-600">取消</button>
          <button @click="handleSubmit" class="px-4 py-2 bg-purple-600 text-white rounded">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import api from '../../api/axios';
import { useAuth } from '../../composables/useAuth';

const { user: currentUser } = useAuth();
const users = ref([]);
const showModal = ref(false);
const editingId = ref(null);
const form = reactive({ username: '', email: '', password: '', role: 'driver' });

const fetchEmployees = async () => {
  try {
    const res = await api.get('/users/?limit=200');
    // 【核心逻辑】排除普通用户，只留员工
    users.value = res.data.filter(u => u.role === 'admin' || u.role === 'driver');
  } catch (e) { console.error(e); }
};

const openCreateModal = () => {
  editingId.value = null;
  Object.assign(form, { username: '', email: '', password: '', role: 'driver' });
  showModal.value = true;
};

const openEditModal = (user) => {
  editingId.value = user.id;
  Object.assign(form, { username: user.username, email: user.email, role: user.role });
  showModal.value = true;
};

const handleSubmit = async () => {
  try {
    if (editingId.value) {
      await api.put(`/users/${editingId.value}`, { username: form.username, role: form.role });
    } else {
      await api.post('/users/', form);
    }
    showModal.value = false;
    fetchEmployees();
    alert('操作成功');
  } catch (e) { alert('操作失败'); }
};

const handleDelete = async (user) => {
  if (user.id === currentUser.value?.id) return alert('不能删除自己');
  if(!confirm(`确定让 ${user.username} 离职吗？`)) return;
  try { await api.delete(`/users/${user.id}`); fetchEmployees(); } catch (e) { alert('失败'); }
};

onMounted(fetchEmployees);
</script>