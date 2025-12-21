// src/composables/useProducts.js
import { ref } from 'vue';
import api from '../api/axios';

// 【关键优化】将状态移出函数，变为全局单例
// 这样无论哪个组件引用，拿到的都是同一份数据，且不会随组件销毁而丢失
const products = ref([]);
const categories = ref([]); // 新增分类缓存
const isLoaded = ref(false); // 标记是否已加载过

export function useProducts() {
  const loading = ref(false);

  // 初始化数据 (带缓存检查)
  const fetchAllData = async (force = false) => {
    // 如果已经加载过且不强制刷新，直接返回，不再请求网络
    if (isLoaded.value && !force && products.value.length > 0) {
      console.log('📦 使用缓存的产品数据');
      return;
    }

    loading.value = true;
    try {
      // 并发请求分类和产品
      const [catRes, prodRes] = await Promise.all([
        api.get('/categories/?limit=100'),
        api.get('/products/?limit=1000')
      ]);

      categories.value = catRes.data;
      products.value = prodRes.data;
      isLoaded.value = true; // 标记已加载

    } catch (error) {
      console.error('获取数据失败:', error);
    } finally {
      loading.value = false;
    }
  };

  return {
    products,
    categories,
    loading,
    isLoaded,
    fetchAllData
  };
}