<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-6">📦 电缆库存管理 (Amazon Cable)</h1>
    
    <div v-if="loading" class="text-center py-10">数据加载中...</div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="product in products" 
        :key="product.id" 
        class="border rounded-lg shadow hover:shadow-lg transition bg-white overflow-hidden"
      >
        <img :src="product.image_url" alt="product" class="w-full h-48 object-cover"/>
        
        <div class="p-4">
          <div class="flex justify-between items-start">
            <h2 class="text-lg font-bold text-gray-800">{{ product.name }}</h2>
            <span class="text-sm px-2 py-1 rounded bg-gray-100 text-gray-600">
              {{ product.category }}
            </span>
          </div>

          <p class="text-gray-500 text-sm mt-2 h-10 line-clamp-2">
            {{ product.description }}
          </p>

          <div class="mt-4 flex justify-between items-center">
            <span class="text-xl font-bold text-orange-600">¥ {{ product.price }}</span>
            
            <div class="flex items-center gap-2">
              <span 
                class="w-3 h-3 rounded-full"
                :class="{
                  'bg-red-500': product.stock === 0,
                  'bg-yellow-500': product.stock > 0 && product.stock < 1000,
                  'bg-green-500': product.stock >= 1000
                }"
              ></span>
              <span class="text-sm font-medium">
                {{ getStockLabel(product.stock) }} ({{ product.stock }})
              </span>
            </div>
          </div>

          <div class="mt-4 pt-4 border-t flex gap-2">
             <button 
               @click="adjustStock(product, 100)"
               class="flex-1 bg-blue-50 text-blue-600 py-1 rounded hover:bg-blue-100 text-sm"
             >
               + 补货
             </button>
             <button 
               @click="adjustStock(product, -100)"
               class="flex-1 bg-gray-50 text-gray-600 py-1 rounded hover:bg-gray-100 text-sm"
             >
               - 出库
             </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getProducts, updateProductStock } from '../api/product'; // 导入刚才写的接口

const products = ref([]);
const loading = ref(true);

// 1. 获取数据
const fetchData = async () => {
  try {
    loading.value = true;
    const response = await getProducts();
    products.value = response.data; // 根据 Axios 响应结构，通常数据在 data 字段
  } catch (error) {
    console.error("无法获取产品数据:", error);
    alert("无法连接到后端，请确保 main.py 正在运行");
  } finally {
    loading.value = false;
  }
};

// 2. 辅助函数：显示库存状态文字
const getStockLabel = (stock) => {
  if (stock === 0) return '排产中';
  if (stock < 1000) return '库存紧张';
  return '库存充足';
};

// 3. 业务逻辑：修改库存
const adjustStock = async (product, amount) => {
  const newStock = product.stock + amount;
  if (newStock < 0) return alert("库存不能小于 0");

  try {
    // 乐观更新：先改前端显示，让体验更快
    product.stock = newStock;
    
    // 发送请求给后端
    await updateProductStock(product.id, { stock: newStock });
    console.log(`产品 ${product.name} 库存已更新为 ${newStock}`);
  } catch (error) {
    // 如果失败，回滚前端显示
    product.stock = product.stock - amount; 
    alert("库存更新失败，请检查是否已登录管理员账号");
  }
};

// 页面加载时拉取数据
onMounted(() => {
  fetchData();
});
</script>