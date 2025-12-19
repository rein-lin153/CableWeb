<template>
  <div class="flex flex-col h-full bg-white rounded-xl shadow-sm border border-gray-100">
    <div class="p-6 border-b border-gray-100 flex justify-between items-center">
      <h2 class="text-xl font-bold text-gray-900 flex items-center">
        <span class="w-2 h-6 bg-green-500 rounded-full mr-3"></span>
        分类层级管理
      </h2>
      <button @click="openModal()" class="bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-600 transition-colors flex items-center">
        <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
        新建根分类
      </button>
    </div>

    <div class="flex-1 overflow-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50 sticky top-0">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase w-20">ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">分类名称结构</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="cat in treeTableData" :key="cat.id" class="hover:bg-gray-50 group">
            <td class="px-6 py-4 text-xs text-gray-400">#{{ cat.id }}</td>
            <td class="px-6 py-4">
              <div class="flex items-center" :style="{ paddingLeft: `${cat.level * 24}px` }">
                <span v-if="cat.level > 0" class="text-gray-300 mr-2">└─</span>
                
                <svg v-if="cat.children && cat.children.length > 0" class="w-4 h-4 text-orange-500 mr-2" fill="currentColor" viewBox="0 0 20 20"><path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"/></svg>
                <svg v-else class="w-4 h-4 text-gray-400 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" /></svg>
                
                <span class="font-medium text-gray-900" :class="{'font-bold': cat.level === 0}">{{ cat.name }}</span>
              </div>
            </td>
            <td class="px-6 py-4 text-right space-x-3 text-sm">
              <button @click="openModal(null, cat.id)" class="text-green-600 hover:underline text-xs flex-inline items-center">
                + 子分类
              </button>
              <button @click="openModal(cat)" class="text-blue-600 hover:underline">编辑</button>
              <button @click="handleDelete(cat)" class="text-red-600 hover:underline">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
        <h3 class="text-lg font-bold mb-4">{{ editingId ? '编辑分类' : '新建分类' }}</h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">上级分类</label>
            <select v-model="form.parent_id" class="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-green-500 outline-none bg-white">
              <option :value="null">无 (作为顶级分类)</option>
              <option 
                v-for="cat in flatOptions" 
                :key="cat.id" 
                :value="cat.id" 
                :disabled="cat.id === editingId"
              >
                {{ cat.label }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">分类名称</label>
            <input v-model="form.name" class="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-green-500 outline-none" placeholder="输入名称，如：电力电缆">
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-6">
          <button @click="showModal = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">取消</button>
          <button @click="handleSubmit" class="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-green-600">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import api from '../../api/axios';

const rawCategories = ref([]); // 后端返回的原始数据（平铺的）
const showModal = ref(false);
const editingId = ref(null);
const form = reactive({ name: '', parent_id: null });

// 获取所有分类 (flat=true)
const fetchCategories = async () => {
  const res = await api.get('/categories/', { params: { flat: true } });
  rawCategories.value = res.data;
};

// === 核心算法：将平铺列表转换为树形结构，再拍平用于表格展示 ===
// 1. 构建树
const buildTree = (items, parentId = null, level = 0) => {
  return items
    .filter(item => item.parent_id === parentId)
    .map(item => ({
      ...item,
      level,
      children: buildTree(items, item.id, level + 1)
    }));
};

// 2. 拍平树 (深度优先遍历，用于 <tr v-for> 显示)
const flattenTree = (tree) => {
  let result = [];
  for (const node of tree) {
    result.push(node);
    if (node.children && node.children.length > 0) {
      result = result.concat(flattenTree(node.children));
    }
  }
  return result;
};

// 计算属性：用于表格渲染的数据 (带 level 属性)
const treeTableData = computed(() => {
  const tree = buildTree(rawCategories.value);
  return flattenTree(tree);
});

// 计算属性：用于 Select 下拉框的数据 (带缩进字符)
const flatOptions = computed(() => {
  return treeTableData.value.map(cat => ({
    id: cat.id,
    label: '　'.repeat(cat.level) + (cat.level > 0 ? '└ ' : '') + cat.name
  }));
});

// === 操作逻辑 ===

const openModal = (cat = null, parentId = null) => {
  if (cat) {
    // 编辑模式
    editingId.value = cat.id;
    form.name = cat.name;
    form.parent_id = cat.parent_id;
  } else {
    // 新建模式 (可能是新建根，也可能是添加子)
    editingId.value = null;
    form.name = '';
    form.parent_id = parentId || null;
  }
  showModal.value = true;
};

const handleSubmit = async () => {
  if (!form.name) return alert('名称不能为空');
  try {
    if (editingId.value) {
      await api.put(`/categories/${editingId.value}`, form);
    } else {
      await api.post('/categories/', form);
    }
    showModal.value = false;
    fetchCategories();
  } catch (e) { alert('操作失败'); }
};

const handleDelete = async (cat) => {
  if (cat.children && cat.children.length > 0) {
    return alert('请先删除或移动该分类下的子分类！');
  }
  if(!confirm(`确定删除 ${cat.name} 吗？`)) return;
  try {
    await api.delete(`/categories/${cat.id}`);
    fetchCategories();
  } catch (e) { alert('删除失败'); }
};

onMounted(fetchCategories);
</script>