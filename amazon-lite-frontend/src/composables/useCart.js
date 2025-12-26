// src/composables/useCart.js
import { ref, computed } from 'vue';
import api from '../api/axios';
import { useAuth } from './useAuth';
import router from '../router';

// 全局状态 (单例模式)，保证不同组件访问到的数据一致
const cartItems = ref([]);
const isCartOpen = ref(false); 
const loading = ref(false);

export function useCart() {
  const { isLoggedIn } = useAuth();

  // 拉取购物车 (核心修复：刷新后调用此方法可恢复数据)
  const fetchCart = async () => {
    if (!isLoggedIn.value) {
      cartItems.value = [];
      return;
    }
    try {
      // 不设置 loading 为 true，避免后台静默同步时页面闪烁
      const res = await api.get('/cart/');
      cartItems.value = res.data;
    } catch (e) {
      console.error("Fetch cart error:", e);
    }
  };

  // 添加商品
  const addToCart = async (variantId, quantity = 1) => {
    if (!isLoggedIn.value) {
      alert('请先登录企业账户');
      router.push('/login');
      return;
    }
    try {
      loading.value = true;
      await api.post('/cart/', { variant_id: variantId, quantity });
      // 添加成功后立即拉取最新状态
      await fetchCart();
      isCartOpen.value = true; // 自动打开购物车反馈
    } catch (e) {
      alert('添加失败: ' + (e.response?.data?.detail || '网络错误'));
    } finally {
      loading.value = false;
    }
  };

  // 🟢 [新功能] 修改数量 (同步后端)
  const updateQuantity = async (itemId, newQuantity) => {
    if (!isLoggedIn.value) return;
    
    // 乐观更新：先在前端修改 UI，让用户感觉“无延迟”
    const itemIndex = cartItems.value.findIndex(i => i.id === itemId);
    const oldQuantity = itemIndex > -1 ? cartItems.value[itemIndex].quantity : 1;
    
    if (itemIndex > -1) {
       if (newQuantity <= 0) {
         // 数量为0，前端先移除
         cartItems.value.splice(itemIndex, 1);
       } else {
         cartItems.value[itemIndex].quantity = newQuantity;
         // 更新小计 (subtotal)
         cartItems.value[itemIndex].subtotal = newQuantity * cartItems.value[itemIndex].price;
       }
    }

    try {
      // 发送请求给后端
      const res = await api.patch(`/cart/${itemId}`, { quantity: newQuantity });
      
      // 如果后端返回 quantity=0 或 404，说明删除了
      if (!res.data || res.data.quantity === 0) {
        if (itemIndex > -1) {
           // 确保前端移除了
           if (cartItems.value.find(i => i.id === itemId)) {
              cartItems.value.splice(itemIndex, 1);
           }
        }
      } else {
        // 更新为后端确认的数据 (价格/库存等可能变动)
        if (itemIndex > -1) {
           Object.assign(cartItems.value[itemIndex], res.data);
        }
      }
    } catch (e) {
      console.error("Update quantity failed:", e);
      // 回滚
      await fetchCart();
      alert("数量更新失败，请重试");
    }
  };

  // 删除商品
  const removeFromCart = async (itemId) => {
    // 复用 updateQuantity 逻辑 (数量设为 0 即删除)
    await updateQuantity(itemId, 0);
  };

  const cartTotal = computed(() => {
    return cartItems.value.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  });

  return {
    cartItems,
    isCartOpen,
    loading,
    cartTotal,
    fetchCart,
    addToCart,
    updateQuantity,
    removeFromCart
  };
}