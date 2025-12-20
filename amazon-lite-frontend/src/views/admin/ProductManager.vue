<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    <div class="mb-6 flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">📦 商品管理</h1>
        <p class="text-sm text-gray-500">管理已上架商品、编辑变体与库存</p>
      </div>
      <button @click="fetchProducts"
        class="bg-gray-100 hover:bg-gray-200 text-gray-600 px-4 py-2 rounded text-sm font-medium">
        刷新列表
      </button>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="th-std">商品名称</th>
            <th class="th-std">分类</th>
            <th class="th-std">包含变体数</th>
            <th class="th-std">总库存</th>
            <th class="th-std">基准价格</th>
            <th class="th-std text-right">操作</th>

            <td class="px-6 py-4 text-right align-middle">
            </td>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="p in products" :key="p.id" class="hover:bg-gray-50">
            <td class="px-6 py-4">
              <div class="flex items-center">
                <img v-if="p.image_url" :src="p.image_url" class="h-10 w-10 rounded bg-gray-100 object-cover mr-3">
                <div>
                  <div class="font-bold text-gray-900">{{ p.name }}</div>
                  <div class="text-xs text-gray-400 truncate w-48">{{ p.description }}</div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 text-sm text-gray-600">
              <span class="bg-gray-100 px-2 py-1 rounded">{{ p.category_detail?.name || '未分类' }}</span>
            </td>
            <td class="px-6 py-4">
              <span
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {{ p.variants.length }} 个规格
              </span>
            </td>
            <td class="px-6 py-4 text-sm font-bold text-gray-700">
              {{p.variants.reduce((acc, v) => acc + v.stock, 0)}}
            </td>
            <td class="px-6 py-4 text-sm text-gray-500">
              ${{ p.price }}
            </td>
            <td class="px-6 py-4 text-right">
              <button @click="openEdit(p)" class="text-indigo-600 hover:text-indigo-900 font-medium">
                编辑变体/库存
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white p-6 rounded-lg w-[800px] max-h-[90vh] overflow-y-auto shadow-2xl">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold text-gray-800">编辑商品: {{ form.name }}</h2>
          <button @click="showModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>

        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div><label class="lbl">商品名称</label><input v-model="form.name" class="input-std"></div>
            <div><label class="lbl">基准价格</label><input v-model.number="form.price" type="number" class="input-std">
            </div>
            <div><label class="lbl">图片链接</label><input v-model="form.image_url" class="input-std"></div>
            <div><label class="lbl">单位</label><input v-model="form.unit" class="input-std"></div>
          </div>
          <div><label class="lbl">描述</label><textarea v-model="form.description" class="input-std"></textarea></div>

          <div class="border-t pt-4 mt-4">
            <div class="flex justify-between items-center mb-2">
              <h3 class="font-bold text-gray-700">🌈 规格与库存管理</h3>
              <button @click="addVariant"
                class="text-sm bg-green-50 text-green-700 px-2 py-1 rounded hover:bg-green-100 border border-green-200">
                + 添加颜色/规格
              </button>
            </div>

            <table class="w-full text-sm border-collapse">
              <thead>
                <tr class="bg-gray-50 text-gray-500 text-left">
                  <th class="p-2 border">规格 (Spec)</th>
                  <th class="p-2 border">颜色</th>
                  <th class="p-2 border">价格 ($)</th>
                  <th class="p-2 border">库存</th>
                  <th class="p-2 border w-10">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(v, idx) in form.variants" :key="idx">
                  <td class="p-2 border"><input v-model="v.spec" class="w-full outline-none bg-transparent"></td>
                  <td class="p-2 border"><input v-model="v.color" class="w-full outline-none bg-transparent"></td>
                  <td class="p-2 border"><input v-model.number="v.price" type="number"
                      class="w-full outline-none bg-transparent"></td>
                  <td class="p-2 border"><input v-model.number="v.stock" type="number"
                      class="w-full outline-none bg-transparent font-bold text-indigo-600"></td>
                  <td class="p-2 border text-center">
                    <button @click="removeVariant(idx)" class="text-red-500 hover:text-red-700">✕</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-6 pt-4 border-t">
          <button @click="showModal = false" class="px-4 py-2 text-gray-500 hover:text-gray-700">取消</button>
          <button @click="handleSave"
            class="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded font-bold shadow">
            保存修改
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import axios from '../../api/axios';

const products = ref([]);
const showModal = ref(false);
const currentId = ref(null);

// 表单数据
const form = reactive({
  name: '', description: '', price: 0, image_url: '', unit: '卷',
  variants: []
});

const fetchProducts = async () => {
  try {
    const res = await axios.get('/products/');
    products.value = res.data;
  } catch (e) { console.error(e); }
};

const openEdit = (p) => {
  currentId.value = p.id;
  form.name = p.name;
  form.description = p.description;
  form.price = p.price;
  form.image_url = p.image_url;
  form.unit = p.unit;
  // 深拷贝变体，防止直接修改显示
  form.variants = p.variants.map(v => ({ ...v }));
  showModal.value = true;
};

const addVariant = () => {
  form.variants.push({
    spec: form.name.split(' ')[0] || '规格', // 智能尝试填充
    color: 'Red',
    price: form.price,
    stock: 100,
    unit: form.unit,
    sku_code: '',
    copper_weight: 0, process_cost: 0
  });
};

const removeVariant = (idx) => {
  form.variants.splice(idx, 1);
};

const handleSave = async () => {
  try {
    await axios.put(`/products/${currentId.value}`, form);
    alert("保存成功！");
    showModal.value = false;
    fetchProducts();
  } catch (e) {
    alert("保存失败: " + e.message);
  }
};

onMounted(() => {
  fetchProducts();
});
</script>

<style scoped>
.th-std {
  /* 去掉 text-left */
  @apply px-6 py-3 text-xs font-medium text-gray-500 uppercase;
}

/* 强制垂直居中 */
td {
  vertical-align: middle;
}

.input-std {
  @apply w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none;
}

.lbl {
  @apply block text-xs font-bold text-gray-500 mb-1;
}
</style>