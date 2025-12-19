import { ref, computed } from 'vue';
import api from '../api/axios';
import { useAuth } from './useAuth';

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

  const submitOrder = async () => {
    loading.value = true;
    try {
      await api.post('/orders/');
      cartItems.value = []; 
      isCartOpen.value = false; 
      alert('订单已提交，请等待后台专员确认价格及发货时间。');
    } catch (e) {
      alert('下单失败：' + (e.response?.data?.detail || '未知错误'));
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