<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">🗂️ 分类架构管理</h1>
      <button @click="openCreate(null)" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg shadow transition">
        + 新建根分类
      </button>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">层级名称</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="cat in flatList" :key="cat.id" class="hover:bg-gray-50 group">
            <td class="px-6 py-4">
              <div :style="{ paddingLeft: (cat.level * 24) + 'px' }" class="flex items-center">
                <span v-if="cat.level > 0" class="text-gray-300 mr-2">└─</span>
                <span class="font-medium" :class="cat.level===0 ? 'text-gray-900 font-bold':'text-gray-700'">
                  {{ cat.name }}
                </span>
              </div>
            </td>
            <td class="px-6 py-4 text-xs text-gray-400">#{{ cat.id }}</td>
            <td class="px-6 py-4 text-right space-x-3 opacity-0 group-hover:opacity-100 transition">
              <button @click="openCreate(cat)" class="text-green-600 hover:text-green-900 text-xs font-bold">+ 添加子类</button>
              <button @click="handleDelete(cat.id)" class="text-red-400 hover:text-red-600 text-xs">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white p-6 rounded-lg w-96 shadow-xl">
        <h3 class="text-lg font-bold mb-4">{{ parentCat ? `在 [${parentCat.name}] 下新建` : '新建根分类' }}</h3>
        <input v-model="formName" class="w-full border p-2 rounded mb-4" placeholder="分类名称" autoFocus>
        <div class="flex justify-end gap-2">
          <button @click="showModal=false" class="px-4 py-2 text-gray-600">取消</button>
          <button @click="handleSave" class="px-4 py-2 bg-indigo-600 text-white rounded">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from '../../api/axios';

const treeData = ref([]);
const showModal = ref(false);
const parentCat = ref(null); // 当前选中的父类
const formName = ref('');

// 将树扁平化以便表格展示 (带 level)
const flatten = (nodes, level = 0) => {
  let res = [];
  for (const node of nodes) {
    res.push({ ...node, level });
    if (node.children && node.children.length) {
      res = res.concat(flatten(node.children, level + 1));
    }
  }
  return res;
};
const flatList = computed(() => flatten(treeData.value));

const fetchTree = async () => {
  const res = await axios.get('/products/categories/tree'); // 注意路径
  treeData.value = res.data;
};

const openCreate = (parent) => {
  parentCat.value = parent;
  formName.value = '';
  showModal.value = true;
};

const handleSave = async () => {
  if (!formName.value) return;
  try {
    await axios.post('/products/categories/', {
      name: formName.value,
      parent_id: parentCat.value ? parentCat.value.id : null
    });
    showModal.value = false;
    fetchTree();
  } catch(e) { alert("失败"); }
};

const handleDelete = async (id) => {
  if(!confirm("确定删除？子分类也会受到影响。")) return;
  await axios.delete(`/products/categories/${id}`);
  fetchTree();
};

onMounted(fetchTree);
</script>