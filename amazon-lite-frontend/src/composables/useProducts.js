// src/composables/useProducts.js
import { ref } from 'vue';
import api from '../api/axios';

export function useProducts() {
  const products = ref([]);
  const loading = ref(false);

  // 1. 获取产品列表 (从后端真实获取)
  const fetchProducts = async () => {
    loading.value = true;
    try {
      // 调用 GET /api/v1/products/
      const response = await api.get('/products/', {
        params: { skip: 0, limit: 100 }
      });
      
      // 将后端返回的真实数据赋值给响应式变量
      products.value = response.data;
      
    } catch (error) {
      console.error('获取产品列表失败:', error);
      // 如果后端没启动或报错，这里 products.value 将保持为空数组
      // 你可以在这里添加 toast 提示用户“网络错误”
    } finally {
      loading.value = false;
    }
  };

  // 2. 更新产品 (调用后端接口修改库存/价格)
  const updateProduct = async (productData) => {
    try {
      // 调用 PUT /api/v1/products/{id}
      // 注意：这里会将整个 product对象传给后端，后端通过 Pydantic 校验并更新
      const response = await api.put(`/products/${productData.id}`, {
        name: productData.name,
        description: productData.description,
        price: productData.price,
        stock: productData.stock,
        category: productData.category,
        image_url: productData.image_url
      });

      // 更新成功后，为了 UI 反应更快，我们手动更新本地列表中的这一项
      // 这样就不需要再次重新拉取整个列表了
      const index = products.value.findIndex(p => p.id === productData.id);
      if (index !== -1) {
        products.value[index] = response.data;
      }
      
      return response.data; // 返回更新后的数据
    } catch (error) {
      console.error('更新产品失败:', error);
      throw error; // 抛出错误，让组件层（ProductManager.vue）去捕获并弹出 Alert
    }
  };

  return {
    products,
    loading,
    fetchProducts,
    updateProduct
  };
}