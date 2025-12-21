import { ref, computed } from 'vue';
import api from '../api/axios';
import { useAuth } from './useAuth';
import router from '../router'; // 【新增】引入路由，以便跳转

// 全局状态
const cartItems = ref([]);
const isCartOpen = ref(false); 
const loading = ref(false);

export function useCart() {
  const { isLoggedIn } = useAuth();

  const fetchCart = async () => {
    if (!isLoggedIn.value) return;
    try {
      const res = await api.get('/cart/');
      cartItems.value = res.data;
    } catch (e) {
      console.error(e);
    }
  };

  const addToCart = async (variantId, quantity = 1) => {
    if (!isLoggedIn.value) {
      alert('请先登录企业账户');
      return;
    }
    try {
      await api.post('/cart/', { variant_id: variantId, quantity });
      await fetchCart(); 
      // 不自动弹出，因为使用了悬浮球
    } catch (e) {
      alert('添加失败');
    }
  };

  const removeFromCart = async (itemId) => {
    try {
      await api.delete(`/cart/${itemId}`);
      cartItems.value = cartItems.value.filter(item => item.id !== itemId);
    } catch (e) {
      console.error(e);
    }
  };

  // 【重写】submitOrder 方法
  const submitOrder = async () => {
    loading.value = true;
    try {
      const res = await api.post('/orders/');
      // 假设后端返回了创建的订单对象，包含 id
      const newOrder = res.data; 
      
      // 1. 清空本地购物车状态
      cartItems.value = [];
      isCartOpen.value = false;
      
      // 2. 友好提示（可选，如果使用了 Toast 组件最好）
      // alert('下单成功！'); 
      
      // 3. 跳转到订单列表或详情页
      router.push('/orders/my');
      
    } catch (e) {
      console.error(e);
      const msg = e.response?.data?.detail || '网络异常';
      alert(`下单失败：${msg}`);
    } finally {
      loading.value = false;
    }
  };

  // 【修复】适配新的后端字段 (item.price)
  const cartTotal = computed(() => {
    if (!cartItems.value) return 0;
    return cartItems.value.reduce((sum, item) => {
      // 优先读取 subtotal (更准)，没有则自己算
      const itemTotal = item.subtotal || (item.price * item.quantity);
      return sum + Number(itemTotal || 0);
    }, 0);
  });

  return {
    cartItems,
    isCartOpen,
    loading,
    cartTotal,
    fetchCart,
    addToCart,
    removeFromCart,
    submitOrder
  };
}