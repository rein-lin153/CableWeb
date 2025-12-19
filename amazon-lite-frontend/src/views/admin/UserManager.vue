<template>
  <div class="flex flex-col h-full bg-white rounded-xl shadow-sm border border-gray-100">
    
    <div class="p-6 border-b border-gray-100 flex justify-between items-center gap-4">
      <h2 class="text-xl font-bold text-gray-900 flex items-center">
        <span class="w-2 h-6 bg-purple-600 rounded-full mr-3"></span>
        人员与权限管理
      </h2>
      
      <div class="flex items-center gap-3">
        <div class="relative w-64 hidden sm:block">
          <input 
            v-model="searchQuery" 
            @keyup.enter="fetchUsers"
            type="text" 
            placeholder="搜索姓名或邮箱..." 
            class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
          <svg class="w-4 h-4 text-gray-400 absolute left-3 top-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        </div>

        <button @click="openCreateModal" class="bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-purple-700 transition-colors flex items-center whitespace-nowrap">
          <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" /></svg>
          新增员工
        </button>
      </div>
    </div>

    <div class="flex-1 overflow-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50 sticky top-0">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">用户/员工</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">角色职位</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">账号状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">注册时间</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-if="loading"><td colspan="5" class="px-6 py-10 text-center text-gray-500">加载中...</td></tr>
          <tr v-else v-for="user in users" :key="user.id" class="hover:bg-gray-50 transition-colors">
            
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="h-9 w-9 rounded-full flex items-center justify-center text-white font-bold mr-3 text-sm shadow-sm"
                     :class="getRoleColor(user.role)">
                  {{ (user.username || user.email).charAt(0).toUpperCase() }}
                </div>
                <div class="flex flex-col">
                  <span class="text-sm font-bold text-gray-900">{{ user.username || '未命名' }}</span>
                  <span class="text-xs text-gray-500">{{ user.email }}</span>
                </div>
              </div>
            </td>

            <td class="px-6 py-4 whitespace-nowrap">
              <span class="px-2.5 py-0.5 rounded-full text-xs font-medium border" :class="getRoleBadgeClass(user.role)">
                {{ getRoleName(user.role) }}
              </span>
            </td>

            <td class="px-6 py-4 whitespace-nowrap">
              <button 
                @click="toggleUserStatus(user)"
                class="px-2 py-1 text-xs font-semibold rounded transition-colors"
                :class="user.is_active ? 'bg-green-100 text-green-700 hover:bg-green-200' : 'bg-red-100 text-red-700 hover:bg-red-200'"
              >
                {{ user.is_active ? '启用中' : '已禁用' }}
              </button>
            </td>

            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ new Date(user.created_at).toLocaleDateString() }}
            </td>

            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-3">
              <button @click="openEditModal(user)" class="text-indigo-600 hover:text-indigo-900">编辑</button>
              <button @click="handleDelete(user)" class="text-red-400 hover:text-red-600" :disabled="user.is_superuser">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white p-6 rounded-xl shadow-xl w-full max-w-md transform transition-all animate-fade-in-up">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-xl font-bold text-gray-900">{{ editingId ? '编辑人员信息' : '录入新员工' }}</h3>
          <button @click="showModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">姓名 / 昵称</label>
            <input v-model="form.username" required type="text" class="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-purple-500 outline-none" placeholder="例如：张师傅">
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">登录邮箱</label>
            <input v-model="form.email" required type="email" :disabled="!!editingId" class="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-purple-500 outline-none disabled:bg-gray-100" placeholder="user@company.com">
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">岗位角色</label>
            <select v-model="form.role" class="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-purple-500 outline-none bg-white">
              <option value="user">普通客户 (User)</option>
              <option value="driver">派送员 (Driver)</option>
              <option value="admin">管理员 (Admin)</option>
            </select>
            <p class="text-xs text-gray-500 mt-1" v-if="form.role === 'driver'">* 派送员将拥有手机端接单权限</p>
            <p class="text-xs text-gray-500 mt-1" v-if="form.role === 'admin'">* 管理员拥有后台所有权限</p>
          </div>

          <div v-if="!editingId">
            <label class="block text-sm font-medium text-gray-700 mb-1">初始密码</label>
            <input v-model="form.password" required type="password" class="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-purple-500 outline-none" placeholder="******">
          </div>

          <div class="flex justify-end gap-3 mt-6">
            <button type="button" @click="showModal = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">取消</button>
            <button type="submit" :disabled="submitting" class="px-6 py-2 bg-gray-900 text-white rounded-lg hover:bg-purple-700 font-medium flex items-center">
              <svg v-if="submitting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              {{ editingId ? '保存更改' : '确认录入' }}
            </button>
          </div>
        </form>
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
const loading = ref(false);
const searchQuery = ref('');

// 弹窗状态
const showModal = ref(false);
const submitting = ref(false);
const editingId = ref(null);
const form = reactive({ email: '', username: '', password: '', role: 'user' });

const fetchUsers = async () => {
  loading.value = true;
  try {
    const params = { skip: 0, limit: 100, search: searchQuery.value || undefined };
    const response = await api.get('/users/', { params });
    users.value = response.data;
  } catch (error) { console.error(error); } finally { loading.value = false; }
};

// 辅助函数
const getRoleName = (role) => {
  const map = { 'admin': '管理员', 'driver': '派送员', 'user': '客户' };
  return map[role] || role;
};

const getRoleColor = (role) => {
  const map = { 'admin': 'bg-purple-600', 'driver': 'bg-indigo-500', 'user': 'bg-gray-400' };
  return map[role] || 'bg-gray-400';
};

const getRoleBadgeClass = (role) => {
  const map = { 
    'admin': 'bg-purple-50 text-purple-700 border-purple-100', 
    'driver': 'bg-indigo-50 text-indigo-700 border-indigo-100', 
    'user': 'bg-gray-50 text-gray-600 border-gray-100' 
  };
  return map[role] || 'bg-gray-100';
};

// 操作逻辑
const openCreateModal = () => {
  editingId.value = null;
  Object.assign(form, { email: '', username: '', password: '', role: 'user' });
  showModal.value = true;
};

const openEditModal = (user) => {
  editingId.value = user.id;
  // 编辑时不需要填密码
  Object.assign(form, { email: user.email, username: user.username, role: user.role });
  showModal.value = true;
};

const handleSubmit = async () => {
  submitting.value = true;
  try {
    if (editingId.value) {
      // 编辑模式
      await api.put(`/users/${editingId.value}`, { 
        username: form.username,
        role: form.role 
      });
      alert('修改成功');
    } else {
      // 新增模式
      await api.post('/users/', form);
      alert('员工录入成功');
    }
    showModal.value = false;
    fetchUsers();
  } catch (e) {
    alert('操作失败: ' + (e.response?.data?.detail || '未知错误'));
  } finally {
    submitting.value = false;
  }
};

const toggleUserStatus = async (user) => {
  if (user.id === currentUser.value?.id) return alert("不能禁用自己");
  try {
    await api.patch(`/users/${user.id}/status`, { is_active: !user.is_active });
    user.is_active = !user.is_active;
  } catch (e) { alert('操作失败'); }
};

const handleDelete = async (user) => {
  if (user.id === currentUser.value?.id) return alert("不能删除自己");
  if (!confirm(`确定删除 ${user.email}?`)) return;
  try {
    await api.delete(`/users/${user.id}`);
    fetchUsers();
  } catch (e) { alert('删除失败'); }
};

onMounted(fetchUsers);
</script>

<style scoped>
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in-up { animation: fadeInUp 0.3s ease-out forwards; }
</style>